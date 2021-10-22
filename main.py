from flask import Flask
from flask import render_template
from flask import request
from flask import flash
from flask import redirect, url_for
import os
from db import get_db
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session, g
from utils import isUsernameValid, isEmailValid, isPasswordValid
import yagmail as yagmail
import random
import functools
from flask import make_response



app = Flask(__name__)
app.secret_key = os.urandom(24)



#--------------------------------------------------------------------------------------------------

# Para confirmar esta logueado o no / bloquea el acceso a dashboard con el login required
@app.route('/')
@app.route('/index')
def index():
    if g.user:
        return redirect( url_for('dashboard') )
    else:    
        return redirect(url_for( 'sesion' ))


# login_required       

def login_required(view):
    @functools.wraps( view ) # toma una función utilizada en un decorador y añadir la funcionalidad de copiar el nombre de la función.
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect( url_for( 'sesion' ) )
        return view( **kwargs )
    return wrapped_view  

# Ruta del dashboard   

@app.route('/Dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    
     
    return render_template("Dashboard.html" ) 
    

# Inicio de session

@app.route('/login', methods=['GET', 'POST'])

def sesion():

        
    if request.method == 'POST':
        db = get_db()
        usuario = request.form['usuario']
        password = request.form['contraseña']

        error = None

        if not usuario:
            error = "Usuario requerido."
            flash(error)
        if not password:
            error = "Contraseña requerida"
            flash(error)

        if error is not None:
            return render_template("sesion.html")
        else:         
            user = db.execute(
                'SELECT id_usuario, usuario, contrasena, rol, email FROM Usuarios WHERE usuario = ?', (usuario,) 
                ).fetchone()
            print(user)
            if user is None:
                error = "Usuario no existe."
                flash(error)
            else:
                password_correcto = check_password_hash(user[2],password)
                if not password_correcto:
                    flash('Usuario y/o contraseña no son correctos.')
                    return render_template("sesion.html",)
                else:
                    session.clear()
                    session['id_usuario'] = user[0]
                    response = make_response( redirect( url_for('dashboard') ) )
                    response.set_cookie( 'username', usuario)
                    
                    return response
                    
                      

   # GET: 
    return render_template("sesion.html"  )
#--------------------------------------------------------------------------------------------------

# Before Request
@app.before_request
def cargar_usuario_registrado():
    print("Entró en before_request.")
    id_usuario = session.get('id_usuario')
    print("id_usuario:", id_usuario)
    if id_usuario is None:
        g.user = None
        
    else:
        g.user = get_db().execute(
            'SELECT id_usuario, usuario, contrasena, rol, email FROM Usuarios WHERE id_usuario = ?'
            ,
            (id_usuario,)
            
        ).fetchone()
    print(g.user)
        
       

#---------------------------------------------------------------------------------------------------


 # para crear usuario
   

@app.route('/sadmin/perfil/crear', methods=['GET', 'POST'])
@login_required
def usuario_super():
    
    try:
        if request.method == 'POST':                  
            usuario = request.form['usuario']
            email = request.form['email']        
            password = str(random.randint(99999,999999))
            rol = request.form['rol'] 
              

            error = None
            db = get_db()
            nom_cookies = request.cookies.get( 'username', 'Usuario')

            if not usuario:
                error = '{}, El Usuario  es requerido.'.format(nom_cookies)
                flash(error)
            if not email:
                error = '{}, El Email es  requerido.'.format(nom_cookies)
                flash(error)
            if not rol:
                error = '{}, El Rol es requerido.'.format(nom_cookies)
                flash(error)  

            if not isUsernameValid(usuario):
                
                error = "El usuario debe ser alfanumerico o incluir solo '.','_','-'"
                flash(error)
            if not isEmailValid(email):
                error = '{}, El Correo es requerido.'.format(nom_cookies)
                flash(error)
                #if not isPasswordValid(password):
                #    error = 'La contraseña debe contener al menos una minúscula, una mayúscula, un número y 8 caracteres'
                #    flash(error)      

            user_email = db.execute(
                'SELECT * FROM Usuarios WHERE email = ? ', (email,) 
                ).fetchone()
            print(user_email)
            if user_email is not None:
                error = '{}, El email ya existe.'.format(nom_cookies)
                flash(error)   
            
            if error is not None:
                return render_template("UsuarioSuper.html")
            else:
            # Seguro:
                password_cifrado = generate_password_hash(password)
                db.execute(
                    'INSERT INTO Usuarios (usuario,contrasena,rol,email) VALUES (?,?,?,?)',
                    (usuario,password_cifrado,rol,email)
                    )
                                
                db.commit()
                flash('{}, Usuario creado.'.format(nom_cookies)) 

                yag = yagmail.SMTP('gabetin@uninorte.edu.co', 'Domayor7') 
                yag.send(to=email, subject='Activa tu cuenta',
                    contents='Bienvenido, revisa el siguiente link e ingresa con su usuario: '+ usuario + ' y contraseña: '  + password + '\n'+ '\n' +'http://127.0.0.1:5000/' )
                                
        return render_template("UsuarioSuper.html")
    except:
        flash('{}, El proceso falló.'.format(nom_cookies))
        return render_template("UsuarioSuper.html")

#---------------------------------------------------------------------------------------------------------
 # Consultar usuarios       

@app.route('/sadmin/usuarios', methods=['GET', 'POST'])
@login_required
def consulta_super():

    if request.method == 'POST':  
        usuario = request.form['usuario']

        if not usuario:
            usuarios = sql_select_usuarios()
        else: 
            db = get_db()
            usuarios = db.execute(
            'SELECT * FROM Usuarios WHERE usuario = ? ', (usuario,) 
            ).fetchall()
            if len(usuarios) < 1 :
               error = "Usuario NO existe."
               flash(error) 
            
            
  
    return render_template("UsuarioSuper.html", usuarios=usuarios)
    

@app.route('/admin/usuarios', methods=['GET', 'POST'])
@login_required
def consulta_admin():

    if request.method == 'POST':  
        usuario = request.form['usuario']

        if not usuario:
            usuarios = sql_select_usuarios()
        else: 
            db = get_db()
            usuarios = db.execute(
            'SELECT * FROM Usuarios WHERE usuario = ? ', (usuario,) 
            ).fetchall()
            if len(usuarios) < 1:
               error = "Usuario NO existe."
               flash(error)            
            
  
    return render_template("UsuarioAdmin.html", usuarios=usuarios)    
    

#------------------------------------------------------------------------------------------------------    
# Para editar usuarios    
   

@app.route('/editarUsuario/<nom_usuario>', methods=['GET', 'POST'])
@login_required
def editar_usuario(nom_usuario):
    if request.method == 'POST':                  
            usuario = request.form['usuario']
            email = request.form['email']  
            rol = request.form['rol'] 

            error = None
            db = get_db()

            if not usuario:
                error = "Usuario requerido."
                flash(error)
            if not email:
                error = "Email requerido."
                flash(error)
            if not rol:
                error = "Rol requerido."
                flash(error)   

                  
            if error is not None:
                return render_template("editarUsuario.html")
            else:
            # Seguro:
                db.execute(
                    'UPDATE Usuarios SET usuario = ?,rol = ?, email = ? WHERE usuario = ?',
                    (usuario,rol,email,usuario)
                    )
                                             
                db.commit()
                flash('Usuario Editado')
                usuarios = db.execute(
                    'SELECT * FROM Usuarios WHERE usuario = ? ', (nom_usuario,) 
                    ).fetchall()
                print(usuarios)   
                return render_template("editarUsuario.html",  usuarios = usuarios , nom_usuario=nom_usuario)
         
    else:
              
        db = get_db()
        usuarios = db.execute(
            'SELECT * FROM Usuarios WHERE usuario = ? ', (nom_usuario,) 
            ).fetchall()
        print(usuarios)   
        return render_template("editarUsuario.html",  usuarios = usuarios , nom_usuario=nom_usuario)

#----------------------------------------------------------------------------------------------------------

#Para Eliminar usuarios

@app.route('/eliminarUsuario/<nom_usuario>', methods=['GET', 'POST'])

@login_required    
def eliminar_usuario(nom_usuario):
    if request.method == 'POST':                  
            usuario = request.form['usuario']        
               

            error = None
            db = get_db()

            if not usuario:
                error = "Usuario requerido."
                flash(error)
                             
            if error is not None:
                return render_template("eliminarUsuario.html")
            else:
            
                db.execute(
                    'DELETE FROM Usuarios WHERE usuario = ?',
                    (usuario,)
                    )
                                            
                db.commit()
                
                return render_template("eliminarMensaje.html")
            


    else:
        db = get_db()
        usuarios = db.execute(
            'SELECT * FROM Usuarios WHERE usuario = ? ', (nom_usuario,) 
            ).fetchall()
        print(usuarios)
        
        return render_template("eliminarUsuario.html",  usuarios = usuarios , nom_usuario=nom_usuario)
                 
       

#----------------------------------------------------------------------------------------

# Crear producto
@app.route('/admin/productos/crear', methods=['GET', 'POST'])
@app.route('/sadmin/productos/crear', methods=['GET', 'POST'])
@login_required
def producto_admin():

    if request.method == 'POST':                  
            codigo = request.form['codigo'].upper()         
            nombre = request.form['nombre'].upper()
            descripcion = request.form['descripcion'].upper()
            cant_minima = request.form['cant_minima']         
            stock = request.form['stock']
            proveedor = request.form['proveedor'].upper()      

            error = None
            db = get_db()

            if not codigo:
                error = "Codigo requerido."
                flash(error)
            if not nombre:
                error = "Nombre requerido."
                flash(error)
            if not descripcion:
                error = "Descripcion requerida."
                flash(error)
            if not cant_minima:
                error = "Cantidad minima requerida."
                flash(error)
            if not stock:
                error = "Stock requerido."
                flash(error)
            if not proveedor:
                error = "Proveedor requerido."
                flash(error)    


            id_proveedor = db.execute(
            'SELECT id_proveedor, nombre,telefono,direccion, ciudad FROM Proveedores WHERE nombre = ?', 
            (proveedor,) 
            ).fetchone()
            print(id_proveedor)

            if id_proveedor is None:
                error = '{}, EL proveedor no existe.'
                flash(error)



            codigo_producto = db.execute(
                'SELECT * FROM Productos WHERE codigo = ? ', (codigo,) 
                ).fetchone()
            print(codigo)
            if codigo_producto is not None:
                error = "El codigo del producto ya existe."
                flash(error)   
            
            if error is not None:
                return render_template("ProductoAdmin.html")
            else:
          
                db.execute(
                    'INSERT INTO Productos (codigo,nombre,descripcion,cant_minima,stock,id_proveedor) VALUES (?,?,?,?,?,?)',
                    (codigo,nombre,descripcion,cant_minima,stock,id_proveedor[0])
                    )
                                
                db.commit()
                flash('Producto creado') 

    return render_template("ProductoAdmin.html") 

#--------------------------------------------------------------------------------------------


 # Consultar productos      

@app.route('/admin/productos', methods=['GET', 'POST'])
@login_required
def consulta_producto_admin():

    if request.method == 'POST':
   

        nombre = request.form['producto'].upper()
        minima =request.values.get('minima')
       
       
              
        if not nombre and  minima == 'minima'  :                         
            db = get_db()
            productos = db.execute(
            'SELECT * FROM Productos INNER JOIN Proveedores ON Productos.id_proveedor = Proveedores.id_Proveedor WHERE stock <  cant_minima'
            ).fetchall()

           
        elif not nombre and  minima is None :            
            db = get_db()
            productos = db.execute(
            'SELECT * FROM Productos INNER JOIN Proveedores ON Productos.id_proveedor = Proveedores.id_Proveedor '
            ).fetchall()
            print(productos)
            
          
        elif nombre and minima == 'minima': 
            flash('La opcion de cantidad minima muestra todos los productos en general cuando tengan un stock por debajo del minimo')
            db = get_db()
            productos = db.execute(
            'SELECT * FROM Productos INNER JOIN Proveedores ON Productos.id_proveedor = Proveedores.id_Proveedor WHERE stock <  cant_minima'
            ).fetchall() 
            
        else: 
            db = get_db()
            productos = db.execute(
            'SELECT * FROM Productos INNER JOIN Proveedores ON Productos.id_proveedor = Proveedores.id_Proveedor WHERE Productos.nombre = ? ', (nombre,) 
            ).fetchall()
          
            if len(productos) < 1 :
               error = "Producto NO existe."
               flash(error)     
    
    return render_template("ProductoAdmin.html", productos=productos )



@app.route('/productos/1', methods=['GET', 'POST'])
@login_required
def consulta_producto_usuario():

    if request.method == 'POST':
   

        nombre = request.form['producto'].upper()
        minima =request.values.get('minima')
       
       
              
        if not nombre and  minima == 'minima'  :                         
            db = get_db()
            productos = db.execute(
            'SELECT * FROM Productos INNER JOIN Proveedores ON Productos.id_proveedor = Proveedores.id_Proveedor WHERE stock <  cant_minima'
            ).fetchall()
        elif not nombre and  minima is None : 
            db = get_db()           
            productos = db.execute(
            'SELECT * FROM Productos INNER JOIN Proveedores ON Productos.id_proveedor = Proveedores.id_Proveedor '
            ).fetchall()
            print(productos)
            
        elif nombre and minima == 'minima': 
            flash('La opcion de cantidad minima muestra todos los productos en general cuando tengan un stock por debajo del minimo')
            db = get_db()
            productos = db.execute(
            'SELECT * FROM Productos INNER JOIN Proveedores ON Productos.id_proveedor = Proveedores.id_Proveedor WHERE stock <  cant_minima'
            ).fetchall()    
        else: 
            db = get_db()
            productos = db.execute(
            'SELECT * FROM Productos INNER JOIN Proveedores ON Productos.id_proveedor = Proveedores.id_Proveedor WHERE Productos.nombre = ? ', (nombre,) 
            ).fetchall()
            if len(productos) < 1 :
               error = "Producto NO existe."
               flash(error)     
    
    return render_template("ProductoUsuario.html", productos=productos) 


#-------------------------------------------------------------------------------------------------


# Para editar pruductos    
   
@app.route('/editarProducto/<nom_producto>', methods=['GET', 'POST'])
@login_required
def editar_producto(nom_producto):
    if request.method == 'POST':  

            codigo = request.form['codigo'].upper()         
            nombre = request.form['nombre'].upper()
            descripcion = request.form['descripcion'].upper()
            cant_minima = request.form['cant_minima']         
            stock = request.form['stock']
            proveedor = request.form['proveedor'].upper()   

            error = None
            db = get_db()

            if not codigo:
                error = "Codigo requerido."
                flash(error)
            if not nombre:
                error = "Nombre requerido."
                flash(error)
            if not descripcion:
                error = "Descripcion requerida."
                flash(error)
            if not cant_minima:
                error = "Cantidad minima requerida."
                flash(error)
            if not stock:
                error = "Stock requerido."
                flash(error)
            if not proveedor:
                error = "Proveedor requerido."
                flash(error)  


            id_proveedor = db.execute(
            'SELECT id_proveedor, nombre,telefono,direccion, ciudad FROM Proveedores WHERE nombre = ?', 
            (proveedor,) 
            ).fetchone()
            print(id_proveedor)

            if id_proveedor is None:
                error = '{}, EL proveedor no existe.'
                flash(error)         

                   
            if error is not None:
                return render_template("editarProducto.html")
            else:         
                db.execute(
                    'UPDATE Productos SET codigo = ?,nombre = ?,descripcion = ?, cant_minima =?, stock = ?, id_proveedor = ? WHERE nombre = ?',
                    (codigo,nombre,descripcion,cant_minima,stock,id_proveedor[0],nombre)
                    )                                             
                db.commit()
                flash('Producto Editado')
                productos = db.execute(
                    'SELECT * FROM Productos INNER JOIN Proveedores ON Productos.id_proveedor = Proveedores.id_Proveedor  WHERE Productos.nombre = ? ', (nom_producto,) 
                    ).fetchall()
                print(productos)   
                return render_template("editarProducto.html",  productos = productos , nom_producto=nom_producto)
         
    else:
              
        db = get_db()
        productos = db.execute(
            'SELECT * FROM Productos INNER JOIN Proveedores ON Productos.id_proveedor = Proveedores.id_Proveedor WHERE  Productos.nombre = ? ', (nom_producto,)
            ).fetchall()
        print(productos)   
        return render_template("editarProducto.html",   productos = productos , nom_producto=nom_producto)


#--------------------------------------------------------------------------------------------


#Para Eliminar producto

@app.route('/eliminarProducto/<nom_producto>', methods=['GET', 'POST'])
@login_required    
def eliminar_producto(nom_producto):
    if request.method == 'POST':                  
            nombre = request.form['nombre'].upper()         
               

            error = None
            db = get_db()

            if not nombre:
                error = "Nombre del producto requerido requerido."
                flash(error)
                             
            if error is not None:
                return render_template("eliminarProducto.html")
            else:
            
                db.execute(
                    'DELETE FROM Productos WHERE nombre = ?',
                    (nombre,)
                    )
                                            
                db.commit()
                
                return render_template("eliminarMensajeProducto.html")
            


    else:
        db = get_db()
        productos = db.execute(
            'SELECT * FROM Productos WHERE nombre = ? ', (nom_producto,) 
            ).fetchall()
        print(productos)
        
        return render_template("eliminarProducto.html",  productos = productos , nom_producto=nom_producto)


#------------------------------------------------------------------------------------------------

# Crear proveedor
@app.route('/admin/proveedores/crear', methods=['GET', 'POST'])
@app.route('/sadmin/proveedores/crear', methods=['GET', 'POST'])
@login_required
def proveedor_admin():

    if request.method == 'POST':                  
                   
            nombre = request.form['nombre'].upper()
            telefono = request.form['telefono'].upper()
            direccion = request.form['direccion'].upper()         
            ciudad = request.form['ciudad'].upper()
                  

            error = None
            db = get_db()

           
            if not nombre:
                error = "Nombre requerido."
                flash(error)
            if not telefono:
                error = "Numero telefonico requerido."
                flash(error)
            if not direccion:
                error = "Direccion requerida."
                flash(error)
            if not ciudad:
                error = "Ciudad requerida."
                flash(error)
                

            nombre_proveedor = db.execute(
                'SELECT * FROM Proveedores WHERE nombre = ? ', (nombre,) 
                ).fetchone()
            print(nombre)
            if nombre_proveedor is not None:
                error = "El nombre del proveedor ya existe."
                flash(error)   
            
            if error is not None:
                return render_template("ProveedorAdmin.html")
            else:          
                db.execute(
                    'INSERT INTO Proveedores (nombre,telefono,direccion,ciudad) VALUES (?,?,?,?)',
                    (nombre,telefono,direccion,ciudad)
                    )
                                
                db.commit()
                flash('Proveedor creado')

    return render_template("ProveedorAdmin.html")   



# Consultar proveedores      

@app.route('/admin/proveedores', methods=['GET', 'POST'])
@login_required
def consulta_proveedor_admin():

    if request.method == 'POST':  
        proveedor = request.form['nombre'].upper()

        if not proveedor:
            proveedores = sql_select_proveedores()
        else: 
            db = get_db()
            proveedores = db.execute(
            'SELECT * FROM Proveedores WHERE nombre = ? ', (proveedor,) 
            ).fetchall()
            if len(proveedores) < 1 :
               error = "Proveedor NO existe."
               flash(error) 
            
            
  
    return render_template("ProveedorAdmin.html", proveedores=proveedores)
    

@app.route('/proveedores/1', methods=['GET', 'POST'])
@login_required
def consulta_proveedor_empleado():

    if request.method == 'POST':  
        proveedor = request.form['nombre'].upper()

        if not proveedor:
            proveedores = sql_select_proveedores()
        else: 
            db = get_db()
            proveedores = db.execute(
            'SELECT * FROM Proveedores WHERE nombre = ? ', (proveedor,) 
            ).fetchall()
            if len(proveedores) < 1 :
               error = "Proveedor NO existe."
               flash(error) 
      
            
  
    return render_template("ProveedorEmpleado.html", proveedores=proveedores)

# Editar proveedor

@app.route('/editarProveedor/<nom_proveedor>', methods=['GET', 'POST'])


@login_required
def editar_proveedor(nom_proveedor):
    if request.method == 'POST':  

            nombre = request.form['nombre'].upper()
            telefono = request.form['telefono'].upper()
            direccion = request.form['direccion'].upper()         
            ciudad = request.form['ciudad'].upper()
                  

            error = None
            db = get_db()

           
            if not nombre:
                error = "Nombre requerido."
                flash(error)
            if not telefono:
                error = "Numero telefonico requerido."
                flash(error)
            if not direccion:
                error = "Direccion requerida."
                flash(error)
            if not ciudad:
                error = "Ciudad requerida."
                flash(error)      

                   
            if error is not None:
                return render_template("editarProveedor.html")
            else:
                          
                db.execute(
                    'UPDATE Proveedores SET nombre = ?, telefono = ?, direccion = ?, ciudad =? WHERE nombre = ?',
                    (nombre,telefono,direccion,ciudad,nombre )
                    )
                                             
                db.commit()
                flash('Proveedor Editado')
                proveedores = db.execute(
                    'SELECT * FROM Proveedores WHERE nombre = ? ', (nom_proveedor,) 
                    ).fetchall()
                print(proveedores)   
                return render_template("editarProveedor.html",  proveedores = proveedores , nom_proveedor=nom_proveedor)
         
    else:
              
        db = get_db()
        proveedores = db.execute(
            'SELECT * FROM Proveedores WHERE nombre = ? ', (nom_proveedor,) 
            ).fetchall()
        print(proveedores)   
        return render_template("editarProveedor.html",    proveedores = proveedores , nom_proveedor=nom_proveedor)


#Para Eliminar proveedor


@app.route('/eliminarProveedor/<nom_proveedor>', methods=['GET', 'POST'])
@login_required    
def eliminar_proveedor(nom_proveedor):
    if request.method == 'POST':                  
            nombre = request.form['nombre'].upper()         
               

            error = None
            db = get_db()

            if not nombre:
                error = "Nombre del proveedor requerido."
                flash(error)
                             
            if error is not None:
                return render_template("eliminarProveedor.html")
            else:
            
                db.execute(
                    'DELETE FROM Proveedores WHERE nombre = ?',
                    (nombre,)
                    )
                                            
                db.commit()
                
                return render_template("eliminarMensajeProveedor.html")
            


    else:
        db = get_db()
        proveedores = db.execute(
            'SELECT * FROM Proveedores WHERE nombre = ? ', (nom_proveedor,) 
            ).fetchall()
        print(proveedores)
        
        return render_template("eliminarProveedor.html",  proveedores = proveedores , nom_proveedor=nom_proveedor)


#------------------------------------------------------------------------------------------------

#Plantillas

   
@app.route('/sadmin/perfil', methods=['GET', 'POST'])
@app.route('/admin/perfil', methods=['GET', 'POST'])
@login_required
def usuario_admin():
    return render_template("UsuarioAdmin.html")    

@app.route('/sadmin/productos', methods=['GET', 'POST'])
@app.route('/productos', methods=['GET', 'POST'])
@login_required
def producto_usuario():
    return render_template("ProductoUsuario.html")

 
@app.route('/sadmin/proveedores', methods=['GET', 'POST'])
@app.route('/proveedores', methods=['GET', 'POST'])
@login_required
def proveedor_empleado():
    return render_template("ProveedorEmpleado.html")   
  


@app.route('/logout')
def logout():
    session.clear()
    return redirect( 'login' )    

#------------------------------------------------------------------------------------------------------

# FUNCIONES  
def sql_select_usuarios():
    sql = "SELECT * FROM Usuarios"
    conn = get_db()
    cursoObj = conn.cursor()
    cursoObj.execute(sql)
    usuarios= cursoObj.fetchall()  # [ [47,"Monitor",368000.0,23], [99,"Mouse",25000.0,64] ]
    print(usuarios)
    return usuarios

def sql_select_productos():
    sql = "SELECT * FROM Productos"
    conn = get_db()
    cursoObj = conn.cursor()
    cursoObj.execute(sql)
    productos= cursoObj.fetchall()  # [ [47,"Monitor",368000.0,23], [99,"Mouse",25000.0,64] ]
    print(productos)
    return productos

def sql_select_proveedores():
    sql = "SELECT * FROM Proveedores"
    conn = get_db()
    cursoObj = conn.cursor()
    cursoObj.execute(sql)
    proveedores= cursoObj.fetchall()  # [ [47,"Monitor",368000.0,23], [99,"Mouse",25000.0,64] ]
    print(proveedores)
    return proveedores




#--------------------------------------------------------------------------------------------------

#Metodo Main
   

if __name__ == "__main__":
    print("Entró en el IF.")
    app.run(debug=True, port=5000)           





    

    