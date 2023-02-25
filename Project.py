from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import pymongo
from bson.objectid import ObjectId
import qrcode
from PIL import Image
import os

MONGO_HOST = 'localhost'
MONGO_PORT = "27017"
MONGO_TIEMPO_FUERA = 1000

MONGO_URI= "mongodb://"+MONGO_HOST+":"+MONGO_PORT+"/"

MONGO_BASEDATOS= "App_QR"
MONGO_COLECCION= "CodigosQR"
client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=MONGO_TIEMPO_FUERA)
baseDatos = client[MONGO_BASEDATOS]
coleccion = baseDatos[MONGO_COLECCION]

def mostrarDatos():
    try:
        registros = tabla.get_children()
        for elemento in registros:
            tabla.delete(elemento)
        for Documento in coleccion.find():
            #tabla.insert('',0,Documento["_id"], values = (Documento["Nombre"],Documento["Codigo"]))
            tabla.insert('',0,text=Documento["_id"],values=(Documento["Nombre"],Documento["Codigo"]))
        #client.close()
    except pymongo.errors.ServerSelectionTimeoutError as error_Tiempo:
        print('Tiempo exedido ', error_Tiempo)
    except pymongo.errors.ConnectionFailure as error_Conexion:
        print('Fallo al conectarse a mongodb ', error_Conexion)

#Funcion para generar el codigo QR
def generarQR():
    try:
        ruta_imagen = './QR_generados/'+Nombre.get()+'.png'
        img = qrcode.make(Codigo.get())
        img.save(ruta_imagen)
        messagebox.showinfo("Generar QR", "Codigo QR generado")
    except FileNotFoundError:
        os.makedirs('./QR_generados/')
        messagebox.showerror("Error","La carpeta QR_generados no existe, (la carpeta se ha creado ahora)\nIntente de nuevo")

#Funciones  para los botones
def crearRegistro():
    if len (Codigo.get())!=0 and len(Nombre.get())!=0:
        try:
            documento={"Codigo":Codigo.get(),"Nombre":Nombre.get()}
            coleccion.insert_one(documento)
            #Actualizar datos de la tabla
            mostrarDatos()
            #Generar codigo
            generarQR()
            #abrir imagen
            ruta_imagen = './QR_generados/'+Nombre.get()+'.png'
            #Image.open(ruta_imagen).show()
            limpiarDatos()
        except pymongo.errors.ConnectionFailure as error:
            print(error)
    else:
        messagebox.showerror("Error","Faltan datos")

#Definir la funcion dobleClicTabla
def dobleClicTabla(event):
    try:
        global ID_Codigo
        ID_Codigo = str(tabla.item(tabla.selection())['text'])
        limpiarDatos()
        documento=coleccion.find({"_id":ObjectId(ID_Codigo)})
        Codigo.insert(0,documento[0]["Codigo"])
        Nombre.insert(0,documento[0]["Nombre"])
        btnCrear["state"] = "disabled"
        btnEditar["state"] = "normal"
        btnBorrar["state"] = "normal"
        btnAbrirqr["state"] = "normal"
    except IndexError:
        messagebox.showerror("Error","Error al editar el elemento con el id: "+ID_Codigo)


def editarRegistro():
    if len (Codigo.get())!=0 and len(Nombre.get())!=0:
        global ID_Codigo
        try:
            idBuscar={"_id":ObjectId(ID_Codigo)}
            nuevosValores = {"Codigo":Codigo.get(),"Nombre":Nombre.get()}
            coleccion.update_one(idBuscar,{"$set":nuevosValores})
            generarQR()
            limpiarDatos()
            mostrarDatos()
        except pymongo.errors.ConnectionFailure as error:
            print(error)
        btnCrear["state"] = "normal"
        btnEditar["state"] = "disabled"
        btnBorrar["state"] = "disabled"
        btnAbrirqr["state"] = "disabled"
    else:
        messagebox.showerror("Error","Faltan datos")

def borrarDatos():
    try:
        global ID_Codigo
        idBuscar={"_id":ObjectId(ID_Codigo)}
        coleccion.delete_one(idBuscar)
        limpiarDatos()
        mostrarDatos()
        btnCrear["state"] = "normal"
        btnEditar["state"] = "disabled"
        btnBorrar["state"] = "disabled"
        btnAbrirqr["state"] = "disabled"
    except pymongo.errors.ConnectionFailure as error:
        print(error)

def limpiarDatos():
    Codigo.delete(0,END)
    Nombre.delete(0,END)
    btnCrear["state"] = "normal"
    btnEditar["state"] = "disabled"
    btnBorrar["state"] = "disabled"
    btnAbrirqr["state"] = "disabled"
    Codigo.focus()

#Abrir imagen del codigo QR
def Abririmagen():
    try:
        ruta_imagen = './QR_generados/'+Nombre.get()+'.png'
        Image.open(ruta_imagen).show()
    except FileNotFoundError:
        messagebox.showerror("Error","La imagen QR no existe\nCreela o actualize la informacion")
def Acerca():
    messagebox.showinfo("Acerca del programa","Trabajo de sustitucion de seminario\nUniversidad Tecnológica de El Salvador\nProgramado por: José Alfonso Escobar Mejía\nCarnet: 25-3188-2022\nFecha: 13/11/2022")

#interfaz grafica de usuario
#----------------Ventana----------------
ventana= Tk()
ventana.title("Generador de codigos QR")
ventana.geometry("602x380")
ventana.minsize(width=603, height=389)
ventana.config(bg="azure3")

#-----------------Rescalavilidad-----------------
ventana.columnconfigure(0, weight=1)
ventana.columnconfigure(1, weight=1)
ventana.columnconfigure(2, weight=1)
ventana.columnconfigure(3, weight=1)
ventana.columnconfigure(4, weight=1)
ventana.columnconfigure(5, weight=1)



#--------------Titulo----------------
Label(ventana,text="Generador de Codigos QR",bg="azure3",font="consolas 25").grid(row=0,column=0,columnspan=6)

#----------------Tabla----------------
tabla=ttk.Treeview(ventana,columns=("Nombre","Codigo"))
#tabla=ttk.Treeview(ventana, columns=2)
tabla.grid(row=1, column=0, columnspan=6)
tabla.heading("#0", text="ID")
tabla.heading("#1", text="Nombre")
tabla.heading("#2", text="Contenido del QR")
#Agregar el evento doble clic
tabla.bind("<Double-Button-1>", dobleClicTabla)
#--------------Etiquetas----------------
#Contenido
Label(ventana,text="Contenido del codigo QR",bg="azure3").grid(row=2,column=0,columnspan=3)
#Fijando la variable nombre en la ventana
Codigo=Entry((ventana))
Codigo.grid(row=2,column=3,columnspan=2,sticky=W+E)
Codigo.focus()

#Nombre del qr
Label(ventana,text="Nombre de la imagen",bg="azure3").grid(row=3,column=0,columnspan=3)
#Fijando la variable sexo en la ventana
Nombre=Entry((ventana))
Nombre.grid(row=3,column=3,columnspan=2,sticky=W+E)



#--------------Botones------------------
#Boton crear
btnCrear= Button(ventana, text="Crear QR",command=crearRegistro, bg="green",fg="black")
btnCrear.grid(row=5,column=1,sticky="nsew",columnspan=2)

#Boton limpiar
btnLimpiar= Button(ventana, text="Limpiar entradas",command=limpiarDatos, bg="AntiqueWhite4",fg="black")
btnLimpiar.grid(row=5,column=3,sticky="nsew",columnspan=2)

#Boton editar
btnEditar= Button(ventana, text="Actualizar QR",command=editarRegistro, bg="SkyBlue4",fg="black")
btnEditar.grid(row=6,column=1,sticky="nsew",columnspan=2)
btnEditar["state"] = "disabled"

#Boton borrar
btnBorrar= Button(ventana, text="Borrar QR",command=borrarDatos, bg="indian red",fg="black")
btnBorrar.grid(row=6,column=3,sticky="nsew",columnspan=2)
btnBorrar["state"] = "disabled"

#Boton abrir codigo qr
btnAbrirqr= Button(ventana, text="Abrir imagen QR",command=Abririmagen, bg="steel blue",fg="black")
btnAbrirqr.grid(row=5,column=5,sticky="nsew",columnspan=1,rowspan=2)
btnAbrirqr["state"] = "disabled"

#------------Acerca de----------------
Acerca_de = Button(ventana, text="Acerca de",command=Acerca ,bg="azure3",fg="black")
Acerca_de.grid(row=7,column=5,sticky="es",columnspan=1)

mostrarDatos()
ventana.mainloop()