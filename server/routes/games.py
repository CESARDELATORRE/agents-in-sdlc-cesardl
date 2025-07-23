from flask import jsonify, Response, Blueprint, request
from models import db, Game, Publisher, Category
from sqlalchemy.orm import Query
from sqlalchemy.exc import IntegrityError

# Create a Blueprint for games routes
games_bp = Blueprint('games', __name__)

def get_games_base_query() -> Query:
    return db.session.query(Game).join(
        Publisher, 
        Game.publisher_id == Publisher.id, 
        isouter=True
    ).join(
        Category, 
        Game.category_id == Category.id, 
        isouter=True
    )

@games_bp.route('/api/games', methods=['GET'])
def get_games() -> Response:
    # Use the base query for all games
    games_query = get_games_base_query().all()
    
    # Convert the results using the model's to_dict method
    games_list = [game.to_dict() for game in games_query]
    
    return jsonify(games_list)

@games_bp.route('/api/games/<int:id>', methods=['GET'])
def get_game(id: int) -> tuple[Response, int] | Response:
    # Use the base query and add filter for specific game
    game_query = get_games_base_query().filter(Game.id == id).first()
    
    # Return 404 if game not found
    if not game_query: 
        return jsonify({"error": "Game not found"}), 404
    
    # Convert the result using the model's to_dict method
    game = game_query.to_dict()
    
    return jsonify(game)

@games_bp.route('/api/games', methods=['POST'])
def create_game() -> tuple[Response, int]:
    try:
        # Get JSON data from request
        data = request.get_json(force=True, silent=True)
        
        if data is None:
            return jsonify({"error": "No data provided"}), 400
        
        # Validate required fields
        required_fields = ['title', 'description', 'category_id', 'publisher_id']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Validate that category and publisher exist
        category = db.session.get(Category, data['category_id'])
        if not category:
            return jsonify({"error": "Category not found"}), 400
            
        publisher = db.session.get(Publisher, data['publisher_id'])
        if not publisher:
            return jsonify({"error": "Publisher not found"}), 400
        
        # Create new game
        new_game = Game(
            title=data['title'],
            description=data['description'],
            category_id=data['category_id'],
            publisher_id=data['publisher_id'],
            star_rating=data.get('star_rating')
        )
        
        # Add and commit to database
        db.session.add(new_game)
        db.session.commit()
        
        # Return the created game
        created_game = get_games_base_query().filter(Game.id == new_game.id).first()
        return jsonify(created_game.to_dict()), 201
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Database integrity error"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500

@games_bp.route('/api/games/<int:id>', methods=['PUT'])
def update_game(id: int) -> tuple[Response, int]:
    try:
        # Get the game to update
        game = db.session.get(Game, id)
        if not game:
            return jsonify({"error": "Game not found"}), 404
        
        # Get JSON data from request
        data = request.get_json(force=True, silent=True)
        
        if data is None:
            return jsonify({"error": "No data provided"}), 400
        
        # Validate foreign keys if provided
        if 'category_id' in data and data['category_id']:
            category = db.session.get(Category, data['category_id'])
            if not category:
                return jsonify({"error": "Category not found"}), 400
                
        if 'publisher_id' in data and data['publisher_id']:
            publisher = db.session.get(Publisher, data['publisher_id'])
            if not publisher:
                return jsonify({"error": "Publisher not found"}), 400
        
        # Update fields if provided
        if 'title' in data:
            game.title = data['title']
        if 'description' in data:
            game.description = data['description']
        if 'category_id' in data:
            game.category_id = data['category_id']
        if 'publisher_id' in data:
            game.publisher_id = data['publisher_id']
        if 'star_rating' in data:
            game.star_rating = data['star_rating']
        
        # Commit changes
        db.session.commit()
        
        # Return the updated game
        updated_game = get_games_base_query().filter(Game.id == id).first()
        return jsonify(updated_game.to_dict()), 200
        
    except ValueError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Database integrity error"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500

@games_bp.route('/api/games/<int:id>', methods=['DELETE'])
def delete_game(id: int) -> tuple[Response, int]:
    try:
        # Get the game to delete
        game = db.session.get(Game, id)
        if not game:
            return jsonify({"error": "Game not found"}), 404
        
        # Delete the game
        db.session.delete(game)
        db.session.commit()
        
        # Return 204 No Content for successful deletion
        return '', 204
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500
