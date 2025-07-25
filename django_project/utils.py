from django.apps import apps

def get_app_models(app_name):
        
    app_models=apps.get_app_config(app_name).get_models()
    return [model.__name__ for model in app_models]

def get_field_names_of_model(app_name, model_name):
    try:
        model=apps.get_model(app_label=app_name,model_name=model_name)
        if model is None:
            raise LookupError(f"model {model_name} idk zmizel")
        fields=model._meta.get_fields()
        return [field.name for field in fields]
    except LookupError as ch:
        print(f"chybka: {ch}")
        return []
    