from base64 import b64encode
from flask import Blueprint, jsonify
from Database.Database import tbl_usuarios, db, tbl_alumnos, tbl_asignaturas, TBL_HORARIOS_ESCOLARES, TBL_HORARIO_ALUMNOS, tbl_docentes, tbl_grados, tbl_grupos, tbl_carreras_tecnicas
from sqlalchemy.exc import SQLAlchemyError

horario_alumnos_bp = Blueprint('horario_alumnos_bp', __name__)

@horario_alumnos_bp.route('/asignaturas/alumno/id/<int:id_usuario>', methods=['GET'])
def get_asignaturas_by_usuario_id(id_usuario):
    try:
        # Buscar el alumno por su ID de usuario
        alumno = tbl_alumnos.query.filter_by(idUsuario=id_usuario).first()
        if not alumno:
            return jsonify({'error': 'Alumno no encontrado'}), 404

        id_alumno = alumno.id_alumnos

        # Obtener los horarios en los que el alumno está inscrito
        horarios = db.session.query(
            TBL_HORARIOS_ESCOLARES.id_horario,
            tbl_asignaturas.nombre_asignatura,
            tbl_docentes.id_docentes,
            tbl_docentes.nombre_docentes,
            tbl_docentes.app_docentes,
            tbl_docentes.apm_docentes,
            tbl_grados.nombre_grado,
            tbl_grupos.nombre_grupos,
            tbl_carreras_tecnicas.nombre_carrera_tecnica,
            TBL_HORARIOS_ESCOLARES.ciclo_escolar,
            TBL_HORARIOS_ESCOLARES.dias_horarios
        ).join(tbl_asignaturas, tbl_asignaturas.id_asignatura == TBL_HORARIOS_ESCOLARES.id_asignatura)\
         .join(tbl_docentes, tbl_docentes.id_docentes == TBL_HORARIOS_ESCOLARES.id_docente)\
         .join(tbl_grados, tbl_grados.id_grado == TBL_HORARIOS_ESCOLARES.id_grado)\
         .join(tbl_grupos, tbl_grupos.id_grupos == TBL_HORARIOS_ESCOLARES.id_grupo)\
         .join(tbl_carreras_tecnicas, tbl_carreras_tecnicas.id_carrera_tecnica == TBL_HORARIOS_ESCOLARES.id_carrera_tecnica)\
         .join(TBL_HORARIO_ALUMNOS, TBL_HORARIO_ALUMNOS.id_horario == TBL_HORARIOS_ESCOLARES.id_horario)\
         .filter(TBL_HORARIO_ALUMNOS.id_alumno == id_alumno).all()

        if not horarios:
            return jsonify([]), 200

        result = []

        for horario in horarios:
            # Obtener el ID del docente y buscar detalles del docente y usuario relacionados
            docente = tbl_docentes.query.filter_by(id_docentes=horario.id_docentes).first()
            if docente:
                usuario_docente = tbl_usuarios.query.filter_by(id_usuario=docente.idUsuario).first()

                # Agregar los datos del docente y usuario
                horario_data = {
                    'id_horario': horario.id_horario,
                    'nombre_asignatura': horario.nombre_asignatura,
                    'nombre_docente': f"{horario.nombre_docentes} {horario.app_docentes} {horario.apm_docentes}",
                    'nombre_grado': horario.nombre_grado,
                    'nombre_grupo': horario.nombre_grupos,
                    'nombre_carrera_tecnica': horario.nombre_carrera_tecnica,
                    'ciclo_escolar': horario.ciclo_escolar,
                    'dias_horarios': eval(horario.dias_horarios) if horario.dias_horarios else [],
                    'docente_telefono': docente.telefono_docentes,
                    'docente_email': usuario_docente.correo_usuario if usuario_docente else 'No disponible',
                    'docente_foto': b64encode(usuario_docente.foto_usuario).decode('utf-8') if usuario_docente and usuario_docente.foto_usuario else None
                }

                result.append(horario_data)

        return jsonify(result), 200

    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500




# Ruta para obtener el horario de un alumno por su ID
@horario_alumnos_bp.route('/horario/<int:alumno_id>', methods=['GET'])
def get_horario(alumno_id):
    try:
        horario = db.session.query(TBL_HORARIO_ALUMNOS, TBL_HORARIOS_ESCOLARES).join(
            TBL_HORARIOS_ESCOLARES, TBL_HORARIO_ALUMNOS.id_horario == TBL_HORARIOS_ESCOLARES.id_horario
        ).filter(TBL_HORARIO_ALUMNOS.id_alumno == alumno_id).all()

        if not horario:
            return jsonify({'message': 'No se encontraron horarios'}), 404

        result = [{
            'id_horario': item.TBL_HORARIOS_ESCOLARES.id_horario,
            'materia': item.TBL_HORARIOS_ESCOLARES.materia,
            'dia': item.TBL_HORARIOS_ESCOLARES.dia,
            'hora_inicio': item.TBL_HORARIOS_ESCOLARES.hora_inicio,
            'hora_fin': item.TBL_HORARIOS_ESCOLARES.hora_fin
        } for item in horario]

        return jsonify(result), 200
    except SQLAlchemyError as e:
        return jsonify({'error': 'Error de la base de datos: ' + str(e)}), 500
    except Exception as e:
        return jsonify({'error': 'Error al obtener el horario: ' + str(e)}), 500
    

# Ruta para visualizar todas las asignaturas del alumno por si id_alumno
@horario_alumnos_bp.route('/asignatura/horario/escolar/<int:id_alumno>', methods=['GET'])
def get_all_asignatura_by_alumno_fam(id_alumno):
    try:
        asignaturas = db.session.query(
            TBL_HORARIO_ALUMNOS.id_horario_alumno,
            TBL_HORARIOS_ESCOLARES.id_horario,
            tbl_asignaturas.nombre_asignatura,
            tbl_docentes.nombre_docentes,
            tbl_docentes.app_docentes,
            tbl_docentes.apm_docentes,
            tbl_carreras_tecnicas.nombre_carrera_tecnica,
            TBL_HORARIOS_ESCOLARES.ciclo_escolar,
            TBL_HORARIOS_ESCOLARES.dias_horarios,
            TBL_HORARIO_ALUMNOS.fecha_inscripcion
        ).join(
            TBL_HORARIOS_ESCOLARES, TBL_HORARIO_ALUMNOS.id_horario == TBL_HORARIOS_ESCOLARES.id_horario
        ).join(
            tbl_asignaturas, TBL_HORARIOS_ESCOLARES.id_asignatura == tbl_asignaturas.id_asignatura
        ).join(
            tbl_docentes, TBL_HORARIOS_ESCOLARES.id_docente == tbl_docentes.id_docentes
        ).join(
            tbl_carreras_tecnicas, TBL_HORARIOS_ESCOLARES.id_carrera_tecnica == tbl_carreras_tecnicas.id_carrera_tecnica
        ).filter(
            TBL_HORARIO_ALUMNOS.id_alumno == id_alumno
        ).all()
        
        if not asignaturas:
            return jsonify({'message': 'No se encontraron asignaturas para el alumno'}), 404
        
        result = [
            {
                'id_horario_alumno': asignatura.id_horario_alumno,
                'nombre_asignatura': asignatura.nombre_asignatura,
                'nombre_docente': f"{asignatura.nombre_docentes} {asignatura.app_docentes} {asignatura.apm_docentes}",
                'nombre_carrera_tecnica': asignatura.nombre_carrera_tecnica,
                'ciclo_escolar': asignatura.ciclo_escolar,
                'dias_horarios': eval(asignatura.dias_horarios) if asignatura.dias_horarios else [],
                
                'id_alumno': id_alumno,
                'fecha_inscripcion': asignatura.fecha_inscripcion.strftime('%Y-%m-%d %H:%M:%S')
            } 
            for asignatura in asignaturas
        ]
        
        return jsonify({'asignaturas': result}), 200
    
    except SQLAlchemyError as e:
        db.session.rollback()  # Deshacer cualquier cambio pendiente
        return jsonify({'error': 'Error de la base de datos: ' + str(e)}), 500
    except Exception as e:
        return jsonify({'error': 'Error al obtener las asignaturas: ' + str(e)}), 500
