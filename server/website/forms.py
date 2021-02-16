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
    age_at_diagnosis = forms.ChoiceField(
        label = "Age at diagnosis",
        choices = [
            (1, 'Younger than 2 years old'),
            (2, '2 years old to 18 years old'),
            (3, 'Older than 18')
        ],
        widget = forms.RadioSelect
    )

    gender = forms.ChoiceField(
        label = "Which sex were you assigned at birth?",
        choices = [
            ("male", "Male"),
            ("female", "Female")
        ],
        widget = forms.RadioSelect
    )

    fev = forms.ChoiceField(
        label = "What is your FEV1?",
        choices = [
            (1, "<30%"),
            (2, "30-39%"),
            (3, "40-49%"),
            (4, "50-59%"),
            (5, "60-69%"),
            (6, "70-79%"),
            (8, ">80%")
        ],
        widget = forms.RadioSelect
    )

    supplemental_oxygen = forms.ChoiceField(
        label = "Use of supplemental oxygen",
        choices = [
            (1, "Yes"),
            (2, "No")
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
        required = False,
        widget = forms.CheckboxSelectMultiple
    )
    exacerbations = forms.IntegerField(
        label = "How many exacerbations have you had in the past year?"
    )


