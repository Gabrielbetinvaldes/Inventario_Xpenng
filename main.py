from flask import Flask
from flask import render_template
from flask import request
from flask import flash
from flask import redirect, url_for
from flask import jsonify
import os
from db import get_db
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session, g
from utils import isUsernameValid, isEmailValid, isPasswordValid
import yagmail as yagmail
import random



app = Flask(__name__)
app.secret_key = os.urandom(24)



#--------------------------------------------------------------------------------------------------

# Inicio de session
@app.route('/', methods=['GET', 'POST'])
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
                'SELECT id, usuario, contrasena, rol FROM Usuarios WHERE usuario = ?', (usuario,) 
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
                    return redirect( 'Dashboard' )   

   # GET: 
    return render_template("sesion.html")
#--------------------------------------------------------------------------------------------------

# Before Request
@app.before_request
def cargar_usuario_registrado():
    print("Entró en before_request.")
    id_usuario = session.get('id_usuario')
    if id_usuario is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT id, usuario, contrasena, rol FROM Usuarios WHERE usuario = ?'
            ,
            (id_usuario,)
        ).fetchone()

#---------------------------------------------------------------------------------------------------


 # para crear usuario   

@app.route('/Dashboard/UsuarioSuper', methods=['GET', 'POST'])
def usuario_super():

    try:
        if request.method == 'POST':                  
            usuario = request.form['usuario'] 
            email = request.form['email']        
            password = str(random.randint(99999,999999))
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

            if not isUsernameValid(usuario):
                error = "El usuario debe ser alfanumerico o incluir solo '.','_','-'"
                flash(error)
            if not isEmailValid(email):
                error = 'Correo invalido'
                flash(error)
                #if not isPasswordValid(password):
                #    error = 'La contraseña debe contener al menos una minúscula, una mayúscula, un número y 8 caracteres'
                #    flash(error)      

            user_email = db.execute(
                'SELECT * FROM Usuarios WHERE email = ? ', (email,) 
                ).fetchone()
            print(user_email)
            if user_email is not None:
                error = "Email ya existe."
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
                flash('Usuario creado') 

                yag = yagmail.SMTP('gabetin@uninorte.edu.co', 'Domayor7') 
                yag.send(to=email, subject='Activa tu cuenta',
                    contents='Bienvenido, revisa el siguiente link e ingresa con su usuario: '+ usuario + ' cd y contraseña: '  + password + '\n'+ '\n' +'http://127.0.0.1:5000/' )
                                
        return render_template("UsuarioSuper.html")
    except:
        flash('Falló en el proceso.')
        return render_template("UsuarioSuper.html")

#---------------------------------------------------------------------------------------------------------
 # Consultar usuarios       

@app.route('/Dashboard/UsuarioSuper/select', methods=['GET', 'POST'])
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
    

@app.route('/Dashboard/UsuarioAdmin/select', methods=['GET', 'POST'])
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
   
@app.route('/Dashboard/UsuarioSuper/editarUsuario/<nom_usuario>', methods=['GET', 'POST'])
@app.route('/Dashboard/UsuarioAdmin/editarUsuario/<nom_usuario>', methods=['GET', 'POST'])
def editar_usuario(nom_usuario):
    if request.method == 'POST':                  
            usuario = request.form['usuario']         
            password = request.form['password']
            rol = request.form['rol']    

            error = None
            db = get_db()

            if not usuario:
                error = "Usuario requerido."
                flash(error)
            if not password:
                error = "Contraseña requerida."
                flash(error)
            if not rol:
                error = "Rol requerido."
                flash(error)   

                  
            if error is not None:
                return render_template("editarUsuario.html")
            else:
            # Seguro:
                password_cifrado = generate_password_hash(password)
                db.execute(
                    'UPDATE Usuarios SET usuario = ?,contrasena = ?,rol = ? WHERE usuario = ?',
                    (usuario,password_cifrado,rol,usuario)
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

@app.route('/Dashboard/UsuarioSuper/eliminarUsuario/<nom_usuario>', methods=['GET', 'POST'])
@app.route('/Dashboard/UsuarioAdmin/eliminarUsuario/<nom_usuario>', methods=['GET', 'POST'])    
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

@app.route('/Dashboard/ProductoAdmin', methods=['GET', 'POST'])
def producto_admin():

    if request.method == 'POST':                  
            codigo = request.form['codigo']         
            nombre = request.form['nombre']
            descripcion = request.form['descripcion']
            cant_minima = request.form['cant_minima']         
            stock = request.form['stock']
            proveedor = request.form['proveedor']      

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
                    (codigo,nombre,descripcion,cant_minima,stock,proveedor)
                    )
                                
                db.commit()
                flash('Producto creado') 

    return render_template("ProductoAdmin.html") 

#--------------------------------------------------------------------------------------------


 # Consultar productos      

@app.route('/Dashboard/ProductoAdmin/select', methods=['GET', 'POST'])
def consulta_producto_admin():

    if request.method == 'POST':
   

        nombre = request.form['producto']
        minima =request.values.get('minima')
       
       
              
        if not nombre and  minima == 'minima'  :                         
            db = get_db()
            productos = db.execute(
            'SELECT * FROM Productos WHERE stock <  cant_minima'
            ).fetchall()
        elif not nombre and  minima is None :            
            productos = sql_select_productos()
        elif nombre and minima == 'minima': 
            flash('La opcion de cantidad minima muestra todos los productos en general cuando tengan un stock por debajo del minimo')
            db = get_db()
            productos = db.execute(
            'SELECT * FROM Productos WHERE stock <  cant_minima'
            ).fetchall()   
        else: 
            db = get_db()
            productos = db.execute(
            'SELECT * FROM Productos WHERE nombre = ? ', (nombre,) 
            ).fetchall()
            if len(productos) < 1 :
               error = "Producto NO existe."
               flash(error)     
    
    return render_template("ProductoAdmin.html", productos=productos)



@app.route('/Dashboard/ProductoUsuario/select', methods=['GET', 'POST'])
def consulta_producto_usuario():

    if request.method == 'POST':
   

        nombre = request.form['producto']
        minima =request.values.get('minima')
       
       
              
        if not nombre and  minima == 'minima'  :                         
            db = get_db()
            productos = db.execute(
            'SELECT * FROM Productos WHERE stock <  cant_minima'
            ).fetchall()
        elif not nombre and  minima is None :            
            productos = sql_select_productos()
        elif nombre and minima == 'minima': 
            flash('La opcion de cantidad minima muestra todos los productos en general cuando tengan un stock por debajo del minimo')
            db = get_db()
            productos = db.execute(
            'SELECT * FROM Productos WHERE stock <  cant_minima'
            ).fetchall()    
        else: 
            db = get_db()
            productos = db.execute(
            'SELECT * FROM Productos WHERE nombre = ? ', (nombre,) 
            ).fetchall()
            if len(productos) < 1 :
               error = "Producto NO existe."
               flash(error)     
    
    return render_template("ProductoUsuario.html", productos=productos) 


#-------------------------------------------------------------------------------------------------


# Para editar pruductos    
   
@app.route('/Dashboard/ProductoAdmin/editarProducto/<nom_producto>', methods=['GET', 'POST'])
@app.route('/Dashboard/ProductoUsuario/editarProducto/<nom_producto>', methods=['GET', 'POST'])
def editar_producto(nom_producto):
    if request.method == 'POST':  

            codigo = request.form['codigo']         
            nombre = request.form['nombre']
            descripcion = request.form['descripcion']
            cant_minima = request.form['cant_minima']         
            stock = request.form['stock']
            proveedor = request.form['proveedor']   

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

                   
            if error is not None:
                return render_template("editarProducto.html")
            else:
            
               
                db.execute(
                    'UPDATE Productos SET codigo = ?,nombre = ?,descripcion = ?, cant_minima =?, stock = ?, proveedor = ? WHERE nombre = ?',
                    (codigo,nombre,descripcion,cant_minima,stock,proveedor,nombre )
                    )
                                             
                db.commit()
                flash('Producto Editado')
                productos = db.execute(
                    'SELECT * FROM Productos WHERE nombre = ? ', (nom_producto,) 
                    ).fetchall()
                print(productos)   
                return render_template("editarProducto.html",  productos = productos , nom_producto=nom_producto)
         
    else:
              
        db = get_db()
        productos = db.execute(
            'SELECT * FROM Productos WHERE nombre = ? ', (nom_producto,) 
            ).fetchall()
        print(productos)   
        return render_template("editarProducto.html",   productos = productos , nom_producto=nom_producto)


#--------------------------------------------------------------------------------------------


#Para Eliminar producto

@app.route('/Dashboard/ProductoAdmin/eliminarProducto/<nom_producto>', methods=['GET', 'POST'])
@app.route('/Dashboard/ProductoUsuario/eliminarProducto/<nom_producto>', methods=['GET', 'POST'])    
def eliminar_producto(nom_producto):
    if request.method == 'POST':                  
            nombre = request.form['nombre']         
               

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

@app.route('/Dashboard/ProveedorAdmin', methods=['GET', 'POST'])
def proveedor_admin():

    if request.method == 'POST':                  
                   
            nombre = request.form['nombre']
            telefono = request.form['telefono']
            direccion = request.form['direccion']         
            ciudad = request.form['ciudad']
                  

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

@app.route('/Dashboard/ProveedorAdmin/select', methods=['GET', 'POST'])
def consulta_proveedor_admin():

    if request.method == 'POST':  
        proveedor = request.form['nombre']

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
    

@app.route('/Dashboard/ProveedorEmpleado/select', methods=['GET', 'POST'])
def consulta_proveedor_empleado():

    if request.method == 'POST':  
        proveedor = request.form['nombre']

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

#------------------------------------------------------------------------------------------------

#Plantillas

@app.route('/Dashboard', methods=['GET', 'POST'])
def dashboard():
    return render_template("Dashboard.html")    

@app.route('/Dashboard/UsuarioAdmin', methods=['GET', 'POST'])
def usuario_admin():
    return render_template("UsuarioAdmin.html")    


@app.route('/Dashboard/ProductoUsuario', methods=['GET', 'POST'])
def producto_usuario():
    return render_template("ProductoUsuario.html")


# ------------------
      

 

@app.route('/Dashboard/ProveedorEmpleado', methods=['GET', 'POST'])
def proveedor_empleado():
    return render_template("ProveedorEmpleado.html")   



@app.route('/Dashboard/ProveedorUsuario/editarProveedor', methods=['GET', 'POST'])
@app.route('/Dashboard/ProveedorAdmin/editarProveedor', methods=['GET', 'POST'])
def editar_proveedor():
    return render_template("editarProveedor.html")    

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


    