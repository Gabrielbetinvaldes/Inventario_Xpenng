function validar_sesion(){  


    usuario = document.getElementById("usuario").value;
    contraseña = document.getElementById("contraseña").value;
  

    
   if (usuario == "") {
        alert("Campo usuario no debe estar vacío.")
        return false;
    }else if ( contraseña == "" ){
        alert("El campo de la clave no debe estar vacío.")
        return false;
    }


    if (usuario == "Grupo7" && contraseña == "Grupo7" ) {       
        window.open('Dashboard', '_blank');
        return false;
     }else {
        alert("Usuario Incorrecto")
        return false;
    }
    
}
function editarUsuario(usuario){

 
   
   window.open("/Dashboard/UsuarioSuper/editarUsuario/"  + usuario +"", "ventana1","width=500,height=500,scrollbars=NO");
     
  
  }
  


 function eliminarUsuario (usuario){
    window.open("/Dashboard/UsuarioSuper/eliminarUsuario/" +usuario+ "","ventana2","width=500,height=300,scrollbars=NO")
 }






 function editarProducto (producto){
    window.open("/Dashboard/ProductoUsuario/editarProducto/"+producto+"","ventana3","width=500,height=700,scrollbars=NO")
 }

 function eliminarProducto(producto){
   window.open("/Dashboard/ProductoUsuario/eliminarProducto/" +producto+ "","ventana2","width=500,height=300,scrollbars=NO")
}

 

 function editarProveedor (proveedor){
    window.open("/Dashboard/ProveedorUsuario/editarProveedor/"+proveedor + "","ventana4","width=500,height=550,scrollbars=NO")
 }

 function eliminarProveedor (proveedor){
   window.open("/Dashboard/ProveedorUsuario/eliminarProveedor/"+proveedor + "","ventana4","width=500,height=550,scrollbars=NO")
}

