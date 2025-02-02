from .models import Clase, Asignatura, OfertaAcademica, Docente, Alumno, NotasClase
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.core import serializers  # https://docs.djangoproject.com/en/3.2/topics/serialization/
from django.contrib.auth.decorators import login_required
from .forms import ImageForm, FormAlumno


@login_required()
def index(request):
    return render(request, 'academico/index.html')


# ---------------------------------------------------------------ALUMNOS-------------------------------------------------------------------------
@login_required()
def alumnos(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            nombre = request.POST.get('nombre')
            apellido = request.POST.get('apellido')
            correo = request.POST.get('correo')
            telefono = request.POST.get('telefono')
            fecha_nacimiento = request.POST.get('datebirth')
            facultad = request.POST.get('facultad')

            Alumno.objects.create(nombre=nombre, apellido=apellido, correo=correo, telefono=telefono,
                                  fecha_nacimiento=fecha_nacimiento, direccion=request.POST.get('dir'),
                                  facultad=facultad)
            form = FormAlumno(request.POST, request.FILES, instance=Alumno.objects.all().order_by('-id').first())
            form.save()

            messages.add_message(request, messages.INFO, f'El alumno {nombre} se ha agregado éxitosamente')

        q = request.GET.get('q')

        if q:
            alumnos = Alumno.objects.filter(nombre__contains=q).order_by('nombre')
        else:
            alumnos = Alumno.objects.all()

        ctx = {
            'activo': 'alumnos',
            'alumnos': alumnos,
            'form': FormAlumno(),
        }

        return render(request, 'academico/alumnos.html', ctx)
    else:
        return redirect(reverse('academico:index'))

@login_required()
def eliminar_alumnos(request, id):
    if request.user.is_superuser:
        messages.add_message(request, messages.INFO, f'El alumno se ha eliminado éxitosamente')
        Alumno.objects.get(pk=id).delete()
        return redirect(reverse('academico:alumnos'))
    else:
        return redirect(reverse('index'))

@login_required()
def editar_alumnos(request, id):
    if request.user.is_superuser:
        if request.method == 'POST':
            nombre = request.POST.get('nombre')
            apellido = request.POST.get('apellido')
            correo = request.POST.get('correo')
            telefono = request.POST.get('telefono')
            fecha_nacimiento = request.POST.get('datebirth')
            facultad = request.POST.get('facultad')

            Alumno.objects.filter(pk=id).update(nombre=nombre, apellido=apellido, correo=correo, telefono=telefono,
                                                fecha_nacimiento=fecha_nacimiento, direccion=request.POST.get('dir'),
                                                facultad=facultad)
            form = FormAlumno(request.POST, request.FILES, instance=Alumno.objects.all().filter(pk=id).first())
            form.save()
            messages.add_message(request, messages.INFO, f'El alumno {nombre} se ha actualizado éxitosamente')

        q = request.GET.get('q')

        if q:
            alumnos = Alumno.objects.filter(nombre__contains=q).order_by('nombre')
        else:
            alumnos = Alumno.objects.all()

        ctx = {
            'activo': 'alumnos',
            'alumnos': alumnos,
            'alumno': get_object_or_404(Alumno, pk=id),
            'form': FormAlumno(),
        }

        return render(request, 'academico/alumnos.html', ctx)
    else:
        return redirect(reverse('academico:index'))


# ---------------------------------------------------------------CLASES-------------------------------------------------------------------------
@login_required()
def clasesAdmin(request):
    if request.user.is_superuser:
        asignaturas = Asignatura.objects.all().order_by('nombre')
        docentes = Docente.objects.all().order_by('nombre')
        dias = ["L", "M", "X", "J", "V", "S", "D"]
        
        if request.method == 'POST':
            asignatura = get_object_or_404(Asignatura, pk=request.POST.get('asignatura'))
            seccion = request.POST.get('seccion')
            hora = request.POST.get('hora')
            aula = request.POST.get('aula')
            cupos = int(request.POST.get('cupos'))
            room = request.POST.get('room')
            seleccionados = []

            print(type(len(seccion)))
            if len(seccion) == 4 and (cupos > 5 and cupos < 61):
                for dia in dias:
                    chk = request.POST.get(f'chk-{dia}')  # almacenar id de clase
                    if dia == chk:
                        seleccionados.append(dia)
            
                resultado = ', '.join(seleccionados) # Para convertir en string al guardar
 
                Clase.objects.create(asignatura=asignatura, seccion=seccion, hora=hora, dias=resultado, aula=aula, cupos=cupos, room=room)
                messages.add_message(request, messages.INFO, f'La clase {asignatura.nombre} ha sido agregada con éxito')
            else:
                messages.add_message(request, messages.ERROR, f'Seccion debe contener 4 digitos, cupos mayor a 10')


        q = request.GET.get('q')

        if q:
            clases = Clase.objects.filter(asignatura__nombre__contains=q).order_by('asignatura')
            # asignatura es unicamente un id, para acceder al nombre de la asignatura se usa doble guion bajo
        else:
            clases = Clase.objects.all().order_by('asignatura')

        ctx = {
            'activo': 'clases',
            'clases': clases,
            'asignaturas': asignaturas,
            'docentes': docentes,
            'q': q,
            'asignarDocente': False
        }
        return render(request, 'academico/clasesAdmin.html', ctx)
    else:
        return redirect(reverse('academico:index'))

@login_required()
def editar_clase(request, id):
    if request.user.is_superuser:
        if request.method == 'POST':
            # docente = get_object_or_404(Docente, pk=request.POST.get('docente'))
            dias = ["L", "M", "X", "J", "V", "S", "D"]
            asignatura = get_object_or_404(Asignatura, pk=request.POST.get('asignatura'))
            seccion = request.POST.get('seccion')
            hora = request.POST.get('hora')
            aula = request.POST.get('aula')
            cupos = request.POST.get('cupos')
            seleccionados = []

            for dia in dias:
                chk = request.POST.get(f'chk-{dia}')  # almacenar id de clase
                if dia == chk:
                    seleccionados.append(dia)

            resultado = ', '.join(seleccionados)  # Para convertir en string al guardar

            Clase.objects.filter(pk=id).update(asignatura=asignatura, seccion=seccion, hora=hora, dias=resultado,
                                               aula=aula,
                                               cupos=cupos)

            messages.add_message(request, messages.INFO, f'La clase {asignatura.nombre} se ha actualizado éxitosamente')

        clase = get_object_or_404(Clase, pk=id)
        asignaturas = Asignatura.objects.all().order_by('nombre')
        clases = Clase.objects.all().order_by('asignatura')

        asignar = True
        if not ((clase.cupos - clase.cupos_disponibles) >= (clase.cupos/2)):
            asignar = False
        
        docentes = Docente.objects.all().order_by('nombre')
        ctx = {
            'activo': 'clases',
            'clases': clases,
            'asignaturas': asignaturas,
            'c': clase,
            'diasClase': clase.dias.split(', '),
            'asignarDocente' : asignar,
            'docentes': docentes
        }

        return render(request, 'academico/clasesAdmin.html', ctx)
    else:
        return redirect(reverse('academico:index'))

@login_required()
def eliminar_clase(request, id):
    messages.add_message(request, messages.INFO, f'La clase se ha eliminado éxitosamente')
    Clase.objects.get(pk=id).delete()
    return redirect(reverse('academico:clasesAdmin'))


# ---------------------------------------------------------------OFERTA PERIODOS-------------------------------------------------------------------------
@login_required()
def periodos_admin(request):
    periodos = OfertaAcademica.objects.all().order_by('-anio', '-periodo')

    ctx = {
        'activo': 'periodos',
        'periodos': periodos,
    }

    return render(request, 'academico/periodosAdmin.html', ctx)

@login_required()
def eliminar_periodo(request, id):
    messages.add_message(request, messages.INFO, f'El periodo se ha eliminado éxitosamente')
    OfertaAcademica.objects.get(pk=id).delete()
    return redirect(reverse('academico:periodosAdmin'))

@login_required()
def editar_periodo(request, id):
    periodo = get_object_or_404(OfertaAcademica, pk=id)
    clases = Clase.objects.all().order_by('asignatura')

    if request.method == 'POST':
        anio = request.POST.get('anio')
        numperiodo = request.POST.get('numperiodo')
        estado = request.POST.get('estado')

        periodo.anio = anio
        periodo.periodo = numperiodo

        if estado:
            periodo.estado = True
        else:
            periodo.estado = False

        for c in clases:
            chk = request.POST.get(f'chk-{c.id}')  # almacenar id de clase
            if str(c.id) == chk:
                # https://stackoverflow.com/questions/50015204/direct-assignment-to-the-forward-side-of-a-many-to-many-set-is-prohibited-use-e
                periodo.clases.add(c.id)
            else:
                # https://docs.djangoproject.com/en/2.2/topics/db/examples/many_to_many/
                periodo.clases.remove(c.id)

        periodo.save()
        messages.add_message(request, messages.INFO, f'La oferta académica ha sido actualizada con éxito')

    ctx = {
        'activo': 'oferta',
        'clases': clases,
        'periodo': periodo,
        'ofertadas': periodo.clases.all()
    }

    return render(request, 'academico/ofertaAdmin.html', ctx)

@login_required()
def agregar_periodo(request):
    if request.method == 'POST':
        anio = request.POST.get('anio')
        periodo = request.POST.get('periodo')
        estado = request.POST.get('estado')

        if estado:
            estado = True
        else:
            estado = False

        OfertaAcademica.objects.create(anio=anio, periodo=periodo, estado=estado)

        messages.add_message(request, messages.INFO, f'El periodo académico ha sido añadido con éxito')

    return redirect(reverse('academico:periodosAdmin'))


# ---------------------------------------------------------------ASIGNATURAS-------------------------------------------------------------------------
def asignaturas(request):
    if request.user.is_superuser:
        try:
            if request.method == 'POST':
                nombre = request.POST.get('nombre')
                descripcion = request.POST.get('descripcion')
                creditos = int(request.POST.get('creditos'))
                
                if creditos > 0 and creditos < 10:
                    c = Asignatura(nombre=nombre, descripcion=descripcion, creditos=creditos)
                    c.save()

                    messages.add_message(request, messages.INFO, f'La asignatura {nombre}  ha sido registrado con éxito')
                else:
                    messages.add_message(request, messages.ERROR,
                                             f'No puede ingresar numeros negativos ni, creditos mayores a 10')
        except:
            pass

        q = request.GET.get('q')

        if q:
            data = Asignatura.objects.filter(nombre__contains=q).order_by('nombre')

        else:
            data = Asignatura.objects.all().order_by('nombre')

        ctx = {
            'asignaturas': data,
            'q': q
        }
        return render(request, 'academico/asignaturas.html', ctx)
    else:
        return redirect(reverse('academico:index'))


def eliminar_asignatura(request, id):
    if request.user.is_superuser:
        Asignatura.objects.get(pk=id).delete()
        messages.add_message(request, messages.INFO, f'La asignatura se ha eliminado éxitosamente')
        return redirect(reverse('asignaturas'))
    else:
        return redirect(reverse('index'))


def editar_asignatura(request, id):
    if request.user.is_superuser:
        asig = get_object_or_404(Asignatura, pk=id)
        try:
            if request.method == 'POST':
                nombre = request.POST.get('nombre')
                descripcion = request.POST.get('descripcion')
                creditos = int(request.POST.get('creditos'))

                if creditos > 0 and creditos < 10:
                    Asignatura.objects.filter(pk=id).update(nombre=nombre, descripcion=descripcion, creditos=creditos)

                    messages.add_message(request, messages.INFO, f'La clase {nombre} se ha actualizado éxitosamente')
                else:
                     messages.add_message(request, messages.ERROR,
                                             f'No puede ingresar numeros negativos, ni creditos mayores a 10')

        except:
            pass

        data = Asignatura.objects.all().order_by('nombre')

        ctx = {
            'activo': 'asignaturas',
            'asignaturas': data,
            'c': asig
        }

        return render(request, 'academico/asignaturas.html', ctx)
    else:
        return redirect(reverse('index'))


def docente_admin(request):
    if request.user.is_superuser:
        if request.method == 'POST':

            Docente.objects.create(nombre=request.POST.get('nombre'), apellido=request.POST.get('apellido'),
                                   telefono=request.POST.get('telefono'), correo=request.POST.get('correo'),
                                   genero=request.POST.get('genero'), fecha_nacimiento=request.POST.get('datebirth'),
                                   fecha_contratacion=request.POST.get('datecon'), direccion=request.POST.get('dir'))

            form = ImageForm(request.POST, request.FILES, instance=Docente.objects.all().order_by('-id').first())
            if form.is_valid():
                form.save()
            messages.add_message(request, messages.INFO, f'El Docente {request.POST.get("nombre")} se ha agregado éxitosamente')

        if request.GET.get('q'):
            docentes = Docente.objects.filter(nombre__contains=request.GET.get('q')).order_by('nombre')
        else:
            docentes = Docente.objects.all()

        ctx = {
            'activo': 'docentes',
            'docentes': docentes,
            'form': ImageForm()

        }

        return render(request, 'academico/docenteAdmin.html', ctx)
    else:
        return redirect(reverse('academico:index'))


def editar_docente(request, id):
    if request.user.is_superuser:
        if request.method == 'POST':
            nombre = request.POST.get('nombre')
            apellido = request.POST.get('apellido')
            telefono = request.POST.get('telefono')
            correo = request.POST.get('correo')
            genero = request.POST.get('genero')
            fecha_nacimiento = request.POST.get('datebirth')
            fecha_contratacion = request.POST.get('datecon')
            dir = request.POST.get('dir')
            Docente.objects.filter(pk=id).update(nombre=nombre, apellido=apellido, telefono=telefono, correo=correo,
                                                 genero=genero, fecha_nacimiento=fecha_nacimiento,
                                                 fecha_contratacion=fecha_contratacion, direccion=dir)
            form = ImageForm(request.POST, request.FILES,
                             instance=Docente.objects.all().filter(pk=id).first())
            form.save()
            messages.add_message(request, messages.INFO, f'El docente {nombre} se ha actualizado éxitosamente')

        if request.GET.get('q'):
            docentes = Docente.objects.filter(nombre__startswith=request.GET.get('q')).order_by('nombre')
        else:
            docentes = Docente.objects.all()
        docente = get_object_or_404(Docente, pk=id)

        ctx = {
            'activo': 'docentes',
            'docentes': docentes,
            'c': docente,
            'form': ImageForm()
        }

        return render(request, 'academico/docenteAdmin.html', ctx)
    else:
        return redirect(reverse('index'))


def eliminar_docente(request, id):
    if request.user.is_superuser:
        messages.add_message(request, messages.INFO, f'El docente se ha eliminado éxitosamente')
        Docente.objects.get(pk=id).delete()
        return redirect(reverse('academico:docenteAdmin'))
    else:
        return redirect(reverse('index'))


def notas(request):
    # TODO: crear vista para que el alumno vea sus notas
    datos = None
    otro = None
    if request.user.groups.exists():
        if request.user.groups.all()[0].name == 'Alumno':
            datos = NotasClase.objects.all().filter(alumno__user=request.user.id)
        # TODO: crear vista para que el docente vea las notas y pueda editarlas
        elif request.user.groups.all()[0].name == 'Docente':
            if request.GET.get('clase'):
                datos = NotasClase.objects.all().filter(clase=request.GET.get('clase'),
                                                        clase__docente__user_id=request.user.id,clase__finalizada=False)
            otro = Clase.objects.all().filter(docente__user=request.user.id,finalizada=False)

    else:
        return redirect(reverse('academico:index'))

    ctx = {
        'activo': 'notas',
        'notas': datos,
        'otro': otro,
    }

    return render(request, 'academico/notas.html', ctx)


def editar_nota(request, id):
    if request.user.groups.exists():
        if request.user.groups.all()[0].name != 'Docente':
            return redirect(reverse('notas'))
        else:
            alumno = None

            try:
                if request.method == 'POST':
                    parcial1, parcial2, parcial3 = int(request.POST.get('parcial1')), int(
                        request.POST.get('parcial2')), int(request.POST.get(
                        'parcial3'))

                    if parcial1 < 101 and parcial2 < 101 and parcial3 < 101 and parcial1 > -1 and parcial2 > -1 and parcial3 > -1:
                        NotasClase.objects.filter(pk=id).update(parcial1=request.POST.get('parcial1'),
                                                                parcial2=request.POST.get('parcial2'),
                                                                parcial3=request.POST.get('parcial3'))
                        messages.add_message(request, messages.SUCCESS, f'La nota se ha actualizado éxitosamente')
                    else:
                        messages.add_message(request, messages.ERROR,
                                             f'No puede haber notas menores a 0 ni mayores a 100')

                alumno = get_object_or_404(NotasClase, pk=id)
                datos = NotasClase.objects.all().filter(clase=alumno.clase,
                                                        clase__docente__user_id=request.user.id)
            except:
                pass



            ctx = {
                'activo': 'notas',
                'notas': datos,
                'c': alumno,
                'otro': Clase.objects.all().filter(docente__user=request.user.id),
            }

            return render(request, 'academico/notas.html', ctx)
    else:
        return redirect(reverse('index'))


# -------------------------------------------------------------OFERTA ALUMNO-------------------------------------------------------------------------
def ofertaAlumno(request):
    oferta = OfertaAcademica.objects.filter(estado=1).last()  # Obtener TODAS las clases ofertadas del periodo activo
    clasesMtr = Clase.objects.filter(alumnos=request.user.alumno.id)  # Clases en las que el alumno esta matriculado actualmente
    asignaturas = []

    
    if oferta:
    # Bucle que ingresa a la lista de asignaturas, unicamente los nombres de las asignaturas ofertadas
        for c in oferta.clases.all().order_by('asignatura'):
            if not c.asignatura.nombre in asignaturas:
                asignaturas.append(c.asignatura.nombre)

        if request.method == 'POST' and request.is_ajax():
            # clases = Clase.objects.all().order_by('asignatura')
            clasesAlumno = request.POST.getlist('clases[]')
            cuposClases = []
            # Matricular el alumno en las clases con los ids ya obtenidos
            for c in oferta.clases.all():
                if f'{c.id}' in clasesAlumno:  # https://parzibyte.me/blog/2018/04/17/python-comprobar-elemento-valor-existe-lista-arreglo/
                    c.alumnos.add(
                        request.user.alumno.id)  # Si el id de la clase existe en las clases que el alumno matriculo, se añade el alumno
                else:
                    c.alumnos.remove(
                        request.user.alumno.id)  # Sino se remueve, en caso de que estuviese matriculado antes y esta vez quitó la clase

                cuposClases.append(c.cupos_disponibles)  # estaran en el mismo orden de las clases en oferta

            return JsonResponse({'clasesAlumno': serializers.serialize("json", oferta.clases.all()),
                                'cupos': cuposClases})  # https://living-sun.com/es/python/713273-sending-json-data-from-view-in-django-python-json-django.html

        # GET
        ctx = {
            'activo': 'matricula',
            'oferta': oferta,
            'asignaturas': asignaturas,
            'clasesOfertadas': oferta.clases.order_by('asignatura', 'seccion'),
            # Clases de la oferta ordenadas por asignatura y seccion
            'clasesAlumno': clasesMtr,
            'srcMin': 'https://cdn.lordicon.com/rivoakkk.json',
            'srcPlus': 'https://cdn.lordicon.com/mecwbjnp.json'
        }
    else:
        ctx = {
            'activo': 'matricula',
            'oferta': oferta,
            'asignaturas': asignaturas,
        }

    return render(request, 'academico/ofertaAlumno.html', ctx)


# -------------------------------------------------------------BOLETA ALUMNO-------------------------------------------
def boletaAlumno(request):
    if request.user.groups.exists():
        if request.user.groups.all()[0].name == 'Alumno':
            data = Clase.objects.filter(alumnos=request.user.alumno.id)

            ctx = {
                'boleta': 'boleta',
                'data': data
            }

            return render(request, 'academico/boletaAlumno.html', ctx)
    else:
        return redirect(reverse('academico:index'))


def editar_perfil_alumnos(request):
    if request.user.groups.exists():
        if request.user.groups.all()[0].name == 'Alumno':
            if request.method == 'POST':
                correo = request.POST.get('correo')
                telefono = request.POST.get('telefono')
                direccion= request.POST.get('direccion')

                if len(telefono) >= 8:
                    Alumno.objects.all().filter(user=request.user.id).update(correo=correo, telefono=telefono, direccion=direccion)
            
                    form = FormAlumno(request.POST,request.FILES,instance=Alumno.objects.all().filter(pk=request.user.alumno.id).first())
                    form.save()
                    messages.add_message(request, messages.INFO, f'Datos actualizados corectamente')
                    
                else:
                    pass
                    messages.add_message(request, messages.INFO, f'Ingrese corectamente su telefono')
                    # debe ser mayor a 8
                    # messages.add_message(request, messages.INFO, f'Tu perfil{User.alumnos.nombre} se ha actualizado éxitosamente')
               
            # GET
            ctx = {
                'activo': 'alumnos',
                'alumnos': alumnos,
                'alumno': get_object_or_404(Alumno, user=request.user.id),
                'o':'si',
                'form': FormAlumno()
            }

            return render(request, 'academico/perfilAlumno.html', ctx)

        elif request.user.groups.all()[0].name == 'Docente':
            if request.method == 'POST':
                correo = request.POST.get('correo')
                telefono = request.POST.get('telefono')
                direccion= request.POST.get('direccion')
                
                if len(telefono) >= 8:
                    Docente.objects.all().filter(user=request.user.id).update(correo=correo, telefono=telefono, direccion=direccion)
                    form = ImageForm(request.POST,request.FILES,instance=Docente.objects.all().filter(pk=request.user.docente.id).first())
                    form.save()
                    messages.add_message(request, messages.INFO, f'Datos actualizados corectamente')
                
                else:
                    messages.add_message(request, messages.INFO, f'Ingrese corectamente su telefono')
                    pass
                    

                # messages.add_message(request, messages.INFO, f'Tu perfil{User.alumnos.nombre} se ha actualizado éxitosamente')
          
            # GET
            ctx = {
                'activo': 'alumnos',
                'alumnos': alumnos,
                'alumno': get_object_or_404(Docente, user=request.user.id),
                'form': ImageForm()
            }

            return render(request, 'academico/perfilAlumno.html', ctx)
    else:
        return redirect(reverse('academico:index'))

 
def clasesdocente(request):
    clases = Clase.objects.all().filter(docente__user=request.user.id)

    if request.method == 'POST':
        for c in clases:
            chk = request.POST.get(f'chk-{c.id}')   
            if chk:
                Clase.objects.filter(pk=c.id).update(finalizada=True)
            else:
                Clase.objects.filter(pk=c.id).update(finalizada=False)
        messages.add_message(request, messages.INFO, f'Datos actualizados correctamente')

            

    clases = Clase.objects.all().filter(docente__user=request.user.id)

    ctx = {
        'clases': clases
    }


    return render(request, 'academico/clasesdocente.html', ctx)


def clasesMatricula(request):
    if request.user.groups.exists():
        if request.user.groups.all()[0].name == 'Alumno':
            datos = Clase.objects.all().filter(alumnos__user_id=request.user.id)
        else:
            datos = Clase.objects.all().filter(docente__user_id=request.user.id)

    ctx = {
        'activo': 'notas',
        'm': datos,

    }

    return render(request, 'academico/clasesMatriculadas.html', ctx)
