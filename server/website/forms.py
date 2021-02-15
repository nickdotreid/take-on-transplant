from django import forms

class WebsiteConfigurationForm(forms.Form):

    FEATURE_FLAGS = [
        ('show_recommended_content', 'Show recommended content'),
        ('show_top_navigation', 'Show top navigation'),
        ('show_content_on_homepage', 'Show homepage content'),
        ('show_survey', 'Show survey')
    ]

    features = forms.MultipleChoiceField(
        label = "Feature Flags",
        choices = FEATURE_FLAGS,
        widget = forms.CheckboxSelectMultiple,
        required = False
    )


class MyCFStageForm(forms.Form):
    fev = forms.ChoiceField(
        label = "What is your FEV1?",
        choices = [
            (0.1, "10%"),
            (0.2, "20%"),
            (0.3, "30%"),
            (0.4, "40%"),
            (0.5, "50%"),
            (0.6, "60%"),
            (0.7, "70%"),
            (0.8, "80%"),
            (0.9, "90%"),
            ( 1, "100%")
        ],
        widget = forms.RadioSelect
    )
    age = forms.IntegerField(
        label = "How old are you?"
    )
    sex = forms.ChoiceField(
        label = "Which sex were you assigned at birth?",
        choices = [
            ("male", "Male"),
            ("female", "Female")
        ],
        widget = forms.RadioSelect
    )
    treatments = forms.MultipleChoiceField(
        label = "Are you using any of the following treatments?",
        choices = [
            (1, "Ivacaftor (Kalydeco)"),
            (2, "Elexacaftor/Tezacaftor/Ivacaftor (Trikafta)"),
            (3, "Using supplemental oxygen")
        ],
        widget = forms.CheckboxSelectMultiple
    )
    exacerbations = forms.IntegerField(
        label = "How many exacerbations have you had in the past year?"
    )


