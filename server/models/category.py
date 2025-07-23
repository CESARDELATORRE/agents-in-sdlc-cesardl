from . import db
from .base import BaseModel
from sqlalchemy.orm import validates, relationship

class Category(BaseModel):
    """
    SQLAlchemy model representing a game category in the crowdfunding platform.
    
    A category has a name and description, and can have many games
    associated with it through a one-to-many relationship.
    """
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    
    # One-to-many relationship: one category has many games
    games = relationship("Game", back_populates="category")
    
    @validates('name')
    def validate_name(self, key, name):
        """
        Validates the category name to ensure it meets minimum length requirements.
        
        Args:
            key (str): The field name being validated
            name (str): The category name to validate
            
        Returns:
            str: The validated category name
            
        Raises:
            ValueError: If the name is too short or invalid
        """
        return self.validate_string_length('Category name', name, min_length=2)
        
    @validates('description')
    def validate_description(self, key, description):
        """
        Validates the category description to ensure it meets minimum length requirements.
        
        Args:
            key (str): The field name being validated
            description (str|None): The description value to validate
            
        Returns:
            str|None: The validated description
            
        Raises:
            ValueError: If the description is too short when provided
        """
        return self.validate_string_length('Description', description, min_length=10, allow_none=True)
    
    def __repr__(self):
        """
        Returns a string representation of the Category object.
        
        Returns:
            str: A formatted string showing the category name
        """
        return f'<Category {self.name}>'
        
    def to_dict(self):
        """
        Converts the Category object to a dictionary representation.
        
        Returns:
            dict: A dictionary containing the category's data including
                  the count of associated games
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'game_count': len(self.games) if self.games else 0
        }