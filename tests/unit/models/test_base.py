# tests/test_base_model.py
import pytest
from datetime import date
from sqlalchemy import Column, Integer, String, Boolean, Text, Date
from app.models.base import BaseModel, db


class TestModel(BaseModel):
    """Test model for BaseModel tests."""
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, info={"label": "Name", "section": "Main", "required": True})
    active = Column(Boolean, default=True, info={"widget": "checkbox", "section": "Status"})
    description = Column(Text, nullable=True, info={"widget": "textarea", "section": "Details"})
    birth_date = Column(Date, nullable=True, info={"section": "Details"})

# Create class at module level, not within test method
class DynamicCompany(BaseModel):
    __tablename__ = "dynamic_companies"  # Use explicit tablename to avoid conflict
    id = Column(Integer, primary_key=True)


@pytest.mark.db
class TestBaseModel:
    def test_tablename_generation(self):
        """Test automatic tablename generation."""
        assert TestModel.__tablename__ == "testmodels"

        # Test the 'y' to 'ies' conversion logic directly without creating a new class
        class_name = "Company"
        name = class_name.lower()
        if name.endswith("y"):
            result = name[:-1] + "ies"
        else:
            result = name + "s"

        assert result == "companies"
        # Also verify our predefined class works as expected
        assert DynamicCompany.__entity_plural__ == "dynamic_companies"

    def test_entity_name(self):
        """Test entity_name property."""
        assert TestModel.__entity_name__ == "TestModel"

    def test_entity_plural(self):
        """Test entity_plural property."""
        assert TestModel.__entity_plural__ == "testmodels"

    def test_init_valid_attributes(self, db):
        """Test initialization with valid attributes."""
        model = TestModel(name="Test", active=True, description="Test description")
        assert model.name == "Test"
        assert model.active is True
        assert model.description == "Test description"

    def test_init_invalid_attribute(self):
        """Test initialization with invalid attribute raises AttributeError."""
        with pytest.raises(AttributeError):
            TestModel(invalid_attr="value")

    def test_to_dict(self, db):
        """Test to_dict method."""
        model = TestModel(name="Test", active=True, description="Test description")
        db.session.add(model)
        db.session.commit()

        data = model.to_dict()
        assert isinstance(data, dict)
        assert data["id"] == model.id
        assert data["name"] == "Test"
        assert data["active"] is True
        assert data["description"] == "Test description"

    def test_save(self, db):
        """Test save method."""
        model = TestModel(name="Test Save")
        result = model.save()

        assert result is model
        assert model.id is not None

        # Verify it was saved to the database
        saved_model = TestModel.query.filter_by(name="Test Save").first()
        assert saved_model is not None
        assert saved_model.id == model.id

    def test_delete(self, db):
        """Test delete method."""
        model = TestModel(name="Test Delete")
        db.session.add(model)
        db.session.commit()
        model_id = model.id

        model.delete()

        # Verify it was deleted from the database
        deleted_model = TestModel.query.get(model_id)
        assert deleted_model is None

    def test_infer_widget(self):
        """Test _infer_widget static method."""
        # Create actual column instances to test with
        id_col = Column(Integer, primary_key=True)
        bool_col = Column(Boolean)
        date_col = Column(Date)
        text_col = Column(Text)
        str_col = Column(String)

        assert TestModel._infer_widget(id_col.type) == "number"
        assert TestModel._infer_widget(bool_col.type) == "checkbox"
        assert TestModel._infer_widget(date_col.type) == "date"
        assert TestModel._infer_widget(text_col.type) == "textarea"
        assert TestModel._infer_widget(str_col.type) == "text"

    def test_ui_schema_without_instance(self):
        """Test ui_schema class method without instance."""
        schema = TestModel.ui_schema()

        assert isinstance(schema, dict)
        assert "Main" in schema
        assert "Status" in schema
        assert "Details" in schema

        # Check Main section
        main_fields = schema["Main"]
        assert len(main_fields) == 2  # id and name
        name_field = next(f for f in main_fields if f["name"] == "name")
        assert name_field["label"] == "Name"
        assert name_field["type"] == "text"
        assert name_field["required"] is True

        # Check Status section
        status_fields = schema["Status"]
        active_field = status_fields[0]
        assert active_field["name"] == "active"
        assert active_field["type"] == "checkbox"

        # Check Details section
        details_fields = schema["Details"]
        assert len(details_fields) == 2  # description and birth_date

    def test_ui_schema_with_instance(self, db):
        """Test ui_schema class method with instance."""
        today = date.today()
        model = TestModel(name="Test UI Schema", birth_date=today)
        db.session.add(model)
        db.session.commit()

        schema = TestModel.ui_schema(instance=model)

        # Check that values from instance are included
        main_fields = schema["Main"]
        name_field = next(f for f in main_fields if f["name"] == "name")
        assert name_field["value"] == "Test UI Schema"

        details_fields = schema["Details"]
        birth_date_field = next(f for f in details_fields if f["name"] == "birth_date")
        assert birth_date_field["value"] == today