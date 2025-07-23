from . import db
from .base import BaseModel
from sqlalchemy.orm import validates, relationship

class Publisher(BaseModel):
    """
    SQLAlchemy model representing a game publisher in the crowdfunding platform.
    
    A publisher has a name and description, and can have many games
    associated with it through a one-to-many relationship.
    """
    __tablename__ = 'publishers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    
    # One-to-many relationship: one publisher has many games
    games = relationship("Game", back_populates="publisher")

    @validates('name')
    def validate_name(self, key, name):
        """
        Validates the publisher name to ensure it meets minimum length requirements.
        
        Args:
            key (str): The field name being validated
            name (str): The publisher name to validate
            
        Returns:
            str: The validated publisher name
            
        Raises:
            ValueError: If the name is too short or invalid
        """
        return self.validate_string_length('Publisher name', name, min_length=2)

    @validates('description')
    def validate_description(self, key, description):
        """
        Validates the publisher description to ensure it meets minimum length requirements.
        
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
        Returns a string representation of the Publisher object.
        
        Returns:
            str: A formatted string showing the publisher name
        """
        return f'<Publisher {self.name}>'

    def to_dict(self):
        """
        Converts the Publisher object to a dictionary representation.
        
        Returns:
            dict: A dictionary containing the publisher's data including
                  the count of associated games
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'game_count': len(self.games) if self.games else 0
        }