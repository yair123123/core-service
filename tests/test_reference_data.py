from decimal import Decimal

from app.db.models.additional_message_template_model import AdditionalMessageTemplateModel
from app.db.models.city_model import CityModel
from app.db.models.price_template_model import PriceTemplateModel


def test_get_reference_data_returns_all_datasets(client, db_session):
    db_session.add_all(
        [
            CityModel(name="Jerusalem", is_active=True),
            CityModel(name="Old City", is_active=False),
            PriceTemplateModel(name="Regular", value=Decimal("50.00"), is_active=True),
            PriceTemplateModel(name="Legacy", value=Decimal("20.00"), is_active=False),
            AdditionalMessageTemplateModel(text="Call before arrival", is_active=True),
            AdditionalMessageTemplateModel(text="Deprecated", is_active=False),
        ]
    )
    db_session.commit()

    response = client.get("/reference-data")

    assert response.status_code == 200
    assert response.json() == {
        "cities": [{"id": 1, "name": "Jerusalem", "isActive": True}],
        "priceTemplates": [{"id": 1, "name": "Regular", "value": "50.00", "isActive": True}],
        "additionalMessageTemplates": [{"id": 1, "text": "Call before arrival", "isActive": True}],
    }


def test_get_reference_data_returns_empty_arrays_for_empty_tables(client):
    response = client.get("/reference-data")

    assert response.status_code == 200
    assert response.json() == {
        "cities": [],
        "priceTemplates": [],
        "additionalMessageTemplates": [],
    }


def test_get_reference_data_individual_endpoints(client, db_session):
    db_session.add_all(
        [
            CityModel(name="Tel Aviv", is_active=True),
            PriceTemplateModel(name="Airport", value=Decimal("120.00"), is_active=True),
            AdditionalMessageTemplateModel(text="Large luggage", is_active=True),
        ]
    )
    db_session.commit()

    cities_response = client.get("/reference-data/cities")
    prices_response = client.get("/reference-data/price-templates")
    messages_response = client.get("/reference-data/additional-message-templates")

    assert cities_response.status_code == 200
    assert prices_response.status_code == 200
    assert messages_response.status_code == 200

    assert cities_response.json() == [{"id": 1, "name": "Tel Aviv", "isActive": True}]
    assert prices_response.json() == [{"id": 1, "name": "Airport", "value": "120.00", "isActive": True}]
    assert messages_response.json() == [{"id": 1, "text": "Large luggage", "isActive": True}]
