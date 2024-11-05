from flask import Blueprint, app, jsonify, request
from Database.Database import   tbl_alumnos, TBL_HORARIO_ALUMNOS, db, tbl_asignaturas, tbl_carreras_tecnicas, tbl_docentes, tbl_grados, tbl_grupos, TBL_HORARIOS_ESCOLARES
from sqlalchemy.exc import SQLAlchemyError
from base64 import b64encode, b64decode
horarios_escolares_bp = Blueprint('horarios_escolares_bp', __name__)

# Ruta para insertar un nuevo horario escolar
@horarios_escolares_bp.route('/horarios_escolares/insert', methods=['POST'])
def create_horario_escolar():
    data = request.get_json()
    id_asignatura = data.get('id_asignatura')
    id_docente = data.get('id_docente')
    id_grado = data.get('id_grado')
    id_grupo = data.get('id_grupo')
    id_carrera_tecnica = data.get('id_carrera_tecnica')
    ciclo_escolar = data.get('ciclo_escolar')
    dias_horarios = data.get('dias_horarios')

    if not all([id_asignatura, id_docente, id_grado, id_grupo, id_carrera_tecnica, ciclo_escolar, dias_horarios]):
        return jsonify({'error': 'Todos los campos son obligatorios'}), 400

    try:
        # Verificar conflictos de horarios
        existing_horarios = db.session.query(TBL_HORARIOS_ESCOLARES).filter(
            TBL_HORARIOS_ESCOLARES.id_docente == id_docente,
            TBL_HORARIOS_ESCOLARES.ciclo_escolar == ciclo_escolar
        ).all()

        for horario in existing_horarios:
            existing_dias_horarios = eval(horario.dias_horarios)
            for new_dia in dias_horarios:
                for existing_dia in existing_dias_horarios:
                    if new_dia['day'] == existing_dia['day']:
                        if not (new_dia['endTime'] <= existing_dia['startTime'] or new_dia['startTime'] >= existing_dia['endTime']):
                            return jsonify({'error': 'Conflicto de horario detectado'}), 409

        # Crear el nuevo horario
        new_horario = TBL_HORARIOS_ESCOLARES(
            id_asignatura=id_asignatura,
            id_docente=id_docente,
            id_grado=id_grado,
            id_grupo=id_grupo,
            id_carrera_tecnica=id_carrera_tecnica,
            ciclo_escolar=ciclo_escolar,
            dias_horarios=str(dias_horarios)  # Asegúrate de almacenar como string
        )

        db.session.add(new_horario)
        db.session.commit()
        return jsonify({'message': 'Horario escolar creado exitosamente'}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Ruta para visualizar todos los horarios escolares
@horarios_escolares_bp.route('/horarios_escolares', methods=['GET'])
def get_all_horarios_escolares():
    try:
        horarios = db.session.query(
            TBL_HORARIOS_ESCOLARES.id_horario,
            tbl_asignaturas.nombre_asignatura,
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
         .all()

        result = [{
            'id_horario': horario.id_horario,
            'nombre_asignatura': horario.nombre_asignatura,
            'nombre_docente': f"{horario.nombre_docentes} {horario.app_docentes} {horario.apm_docentes}",
            'nombre_grado': horario.nombre_grado,
            'nombre_grupo': horario.nombre_grupos,
            'nombre_carrera_tecnica': horario.nombre_carrera_tecnica,
            'ciclo_escolar': horario.ciclo_escolar,
            'dias_horarios': eval(horario.dias_horarios) if horario.dias_horarios else []
        } for horario in horarios]

        return jsonify(result), 200
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500

# Ruta para actualizar un horario escolar
@horarios_escolares_bp.route('/horarios_escolares/update/<int:id>', methods=['PUT'])
def update_horario_escolar(id):
    data = request.get_json()
    try:
        horario = TBL_HORARIOS_ESCOLARES.query.get(id)
        if not horario:
            return jsonify({'error': 'Horario no encontrado'}), 404

        horario.id_asignatura = data.get('id_asignatura')
        horario.id_docente = data.get('id_docente')
        horario.id_grado = data.get('id_grado')
        horario.id_grupo = data.get('id_grupo')
        horario.id_carrera_tecnica = data.get('id_carrera_tecnica')
        horario.ciclo_escolar = data.get('ciclo_escolar')
        horario.dias_horarios = str(data.get('dias_horarios'))  # Asegúrate de almacenar como string

        db.session.commit()
        return jsonify({'message': 'Horario actualizado exitosamente'}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        app.logger.error(f"Error de SQLAlchemy: {str(e)}")
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        app.logger.error(f"Error inesperado: {str(e)}")
        return jsonify({'error': str(e)}), 500


# Ruta para eliminar un horario escolar
@horarios_escolares_bp.route('/horarios_escolares/delete/<int:id>', methods=['DELETE'])
def delete_horario_escolar(id):
    try:
        horario = TBL_HORARIOS_ESCOLARES.query.get(id)
        if not horario:
            return jsonify({'error': 'Horario no encontrado'}), 404

        db.session.delete(horario)
        db.session.commit()
        return jsonify({'message': 'Horario eliminado exitosamente'}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@horarios_escolares_bp.route('/horarios_escolares/docente/<int:id_usuario>', methods=['GET'])
def get_horarios_by_docente(id_usuario):
    try:
        docente = tbl_docentes.query.filter_by(idUsuario=id_usuario).first()
        if not docente:
            return jsonify({'error': 'Docente no encontrado'}), 404

        horarios = db.session.query(
            TBL_HORARIOS_ESCOLARES.id_horario,
            tbl_asignaturas.nombre_asignatura,
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
         .filter(TBL_HORARIOS_ESCOLARES.id_docente == docente.id_docentes)\
         .all()

        result = [{
            'id_horario': horario.id_horario,
            'nombre_asignatura': horario.nombre_asignatura,
            'nombre_docente': f"{horario.nombre_docentes} {horario.app_docentes} {horario.apm_docentes}",
            'nombre_grado': horario.nombre_grado,
            'nombre_grupo': horario.nombre_grupos,
            'nombre_carrera_tecnica': horario.nombre_carrera_tecnica,
            'ciclo_escolar': horario.ciclo_escolar,
            'dias_horarios': eval(horario.dias_horarios) if horario.dias_horarios else []
        } for horario in horarios]

        return jsonify(result), 200
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500



# Ruta para agregar un alumno a un horario específico
@horarios_escolares_bp.route('/horarios_escolares/<int:id_horario>/agregar_alumno', methods=['POST'])
def add_alumno_to_horario(id_horario):
    data = request.get_json()
    nocontrol_alumno = data.get('nocontrol_alumnos')

    if not nocontrol_alumno:
        return jsonify({'error': 'El número de control del alumno es obligatorio'}), 400

    try:
        alumno = tbl_alumnos.query.filter_by(nocontrol_alumnos=nocontrol_alumno).first()
        if not alumno:
            return jsonify({'error': 'Alumno no encontrado'}), 404

        existing_record = TBL_HORARIO_ALUMNOS.query.filter_by(id_horario=id_horario, id_alumno=alumno.id_alumnos).first()
        if existing_record:
            return jsonify({'error': 'El alumno ya está inscrito en este horario'}), 409

        nuevo_horario_alumno = TBL_HORARIO_ALUMNOS(id_horario=id_horario, id_alumno=alumno.id_alumnos)
        db.session.add(nuevo_horario_alumno)
        db.session.commit()

        return jsonify({'message': 'Alumno agregado exitosamente al horario'}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

    
# Ruta para obtener los alumnos de un horario específico
@horarios_escolares_bp.route('/alumnos/horario/<int:id_horario>', methods=['GET'])
def get_alumnos_by_horario(id_horario):
    try:
        alumnos = db.session.query(
            tbl_alumnos.id_alumnos,
            tbl_alumnos.nombre_alumnos,
            tbl_alumnos.app_alumnos,
            tbl_alumnos.apm_alumnos,
            tbl_alumnos.nocontrol_alumnos,
            tbl_alumnos.foto_alumnos,
            tbl_carreras_tecnicas.nombre_carrera_tecnica,
            tbl_grados.nombre_grado,
            tbl_grupos.nombre_grupos
        ).join(TBL_HORARIO_ALUMNOS, tbl_alumnos.id_alumnos == TBL_HORARIO_ALUMNOS.id_alumno)\
         .join(tbl_carreras_tecnicas, tbl_alumnos.idCarreraTecnica == tbl_carreras_tecnicas.id_carrera_tecnica)\
         .join(tbl_grados, tbl_alumnos.idGrado == tbl_grados.id_grado)\
         .join(tbl_grupos, tbl_alumnos.idGrupo == tbl_grupos.id_grupos)\
         .filter(TBL_HORARIO_ALUMNOS.id_horario == id_horario).all()

        if not alumnos:
            return jsonify([]), 200

        result = [{
            'id_alumnos': alumno.id_alumnos,
            'nombre_alumnos': alumno.nombre_alumnos,
            'app_alumnos': alumno.app_alumnos,
            'apm_alumnos': alumno.apm_alumnos,
            'nocontrol_alumnos': alumno.nocontrol_alumnos,
            'foto_alumnos': b64encode(alumno.foto_alumnos).decode('utf-8') if alumno.foto_alumnos else None,
            'nombre_carrera_tecnica': alumno.nombre_carrera_tecnica,
            'nombre_grado': alumno.nombre_grado,
            'nombre_grupo': alumno.nombre_grupos,
        } for alumno in alumnos]

        return jsonify(result), 200
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500

    





#CODIGO PARA ALEXA
@horarios_escolares_bp.route('/horarios_escolares/alumno/no_control/<string:nocontrol>', methods=['GET'])
def get_horario_by_alumno_no_control(nocontrol):
    try:
        alumno = tbl_alumnos.query.filter_by(nocontrol_alumnos=nocontrol).first()
        if not alumno:
            return jsonify({'error': 'Alumno no encontrado'}), 404

        horarios = db.session.query(
            TBL_HORARIOS_ESCOLARES.id_horario,
            tbl_asignaturas.nombre_asignatura,
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
         .filter(TBL_HORARIO_ALUMNOS.id_alumno == alumno.id_alumnos).all()

        if not horarios:
            return jsonify({'error': 'Horarios no encontrados para el alumno'}), 404

        result = [{
            'id_horario': horario.id_horario,
            'nombre_asignatura': horario.nombre_asignatura,
            'nombre_docente': f"{horario.nombre_docentes} {horario.app_docentes} {horario.apm_docentes}",
            'nombre_grado': horario.nombre_grado,
            'nombre_grupo': horario.nombre_grupos,
            'nombre_carrera_tecnica': horario.nombre_carrera_tecnica,
            'ciclo_escolar': horario.ciclo_escolar,
            'dias_horarios': eval(horario.dias_horarios) if horario.dias_horarios else []
        } for horario in horarios]

        return jsonify(result), 200
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500

