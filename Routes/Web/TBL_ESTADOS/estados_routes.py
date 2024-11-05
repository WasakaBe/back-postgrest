from flask import Blueprint, jsonify, request
from Database.Database import db, tbl_estados
from base64 import b64encode, b64decode
from sqlalchemy.exc import SQLAlchemyError

estados_bp = Blueprint('estados_bp', __name__)

# Ruta para obtener todos los estados
@estados_bp.route('/estados', methods=['GET'])
def get_all_estados():
    try:
        estados = tbl_estados.query.all()
        result = [{'id_estado': estado.id_estado,
                   'nombre_estado': estado.nombre_estado,
                   'foto_estado': b64encode(estado.foto_estado).decode('utf-8') if estado.foto_estado else None
                   } for estado in estados]
        return jsonify({'estados': result})
    except Exception as e:
        print(f'Error al obtener los estados: {str(e)}')
        return jsonify({'message': 'Error al obtener los estados', 'error': str(e)}), 500

# Ruta para eliminar un estado por su ID
@estados_bp.route('/estados/<int:id>', methods=['DELETE'])
def delete_estado(id):
    estado = tbl_estados.query.get(id)
    if not estado:
        return jsonify({'message': 'Estado no encontrado'}), 404

    try:
        db.session.delete(estado)
        db.session.commit()
        return jsonify({'message': 'Estado eliminado exitosamente'})
    except Exception as e:
        print(f'Error al eliminar el estado: {str(e)}')
        return jsonify({'message': 'Error al eliminar el estado', 'error': str(e)}), 500

# Ruta para insertar un nuevo estado
@estados_bp.route('/estados', methods=['POST'])
def insert_estado():
    data = request.json
    if not data:
        return jsonify({'message': 'No se proporcionaron datos para insertar'}), 400

    try:
        nombre_estado = data.get('nombre_estado')
        if tbl_estados.query.filter_by(nombre_estado=nombre_estado).first():
            return jsonify({'message': f'El estado "{nombre_estado}" ya está registrado. No se pueden repetir nombres de estado.'}), 400

        nuevo_estado = tbl_estados(
            nombre_estado=nombre_estado,
            foto_estado=b64decode(data.get('foto_estado').encode('utf-8')) if data.get('foto_estado') else None
        )
        db.session.add(nuevo_estado)
        db.session.commit()
        return jsonify({'message': 'Estado insertado exitosamente'}), 201
    except Exception as e:
        print(f'Error al insertar el estado: {str(e)}')
        return jsonify({'message': 'Error al insertar el estado', 'error': str(e)}), 500

# Ruta para actualizar un estado por su ID
@estados_bp.route('/estados/<int:id>', methods=['PUT'])
def update_estado(id):
    data = request.json
    if not data:
        return jsonify({'message': 'No se proporcionaron datos para actualizar'}), 400

    estado = tbl_estados.query.get(id)
    if not estado:
        return jsonify({'message': 'Estado no encontrado'}), 404

    try:
        estado.nombre_estado = data.get('nombre_estado', estado.nombre_estado)
        if foto_estado := data.get('foto_estado'):
            estado.foto_estado = b64decode(foto_estado.encode('utf-8'))

        db.session.commit()
        return jsonify({'message': 'Estado actualizado exitosamente'})
    except Exception as e:
        print(f'Error al actualizar el estado: {str(e)}')
        return jsonify({'message': 'Error al actualizar el estado', 'error': str(e)}), 500
