from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import Escola, CustomUser, Responsavel, Aluno, ResponsavelPeloAluno, NecessidadeEspecial, ModalidadeEnsino, SerieAno


class CustomAuthenticationForm(AuthenticationForm):
    tipo_usuario = forms.ChoiceField(choices=CustomUser.TIPO_USUARIO_CHOICES, required=True)
    escola = forms.ModelChoiceField(queryset=Escola.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        super(CustomAuthenticationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Email'})
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['tipo_usuario'].widget.attrs.update({'class': 'form-control'})
        self.fields['escola'].widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        tipo_usuario = cleaned_data.get('tipo_usuario')
        escola = cleaned_data.get('escola')
        user = CustomUser.objects.filter(username=username).first()

        if user and tipo_usuario == CustomUser.AGENTE_ADMINISTRATIVO and not escola:
            raise forms.ValidationError('Agente Administrativo deve selecionar uma escola.')
        return cleaned_data

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    tipo_usuario = forms.ChoiceField(choices=CustomUser.TIPO_USUARIO_CHOICES, required=True)
    escola = forms.ModelChoiceField(queryset=Escola.objects.all(), required=False)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'tipo_usuario', 'escola']

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        self.fields['tipo_usuario'].widget.attrs.update({'class': 'form-control'})
        self.fields['escola'].widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = super().clean()
        tipo_usuario = cleaned_data.get('tipo_usuario')
        escola = cleaned_data.get('escola')
        if tipo_usuario == CustomUser.AGENTE_ADMINISTRATIVO and not escola:
            self.add_error('escola', 'Agente Administrativo deve selecionar uma escola.')
        return cleaned_data

class CustomUserLoginForm(forms.Form):
    username = forms.CharField(max_length=255, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    tipo_usuario = forms.ChoiceField(choices=CustomUser.TIPO_USUARIO_CHOICES, required=True)
    escola = forms.ModelChoiceField(queryset=Escola.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        super(CustomUserLoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password'].widget.attrs.update({'class': 'form-control'})
        self.fields['tipo_usuario'].widget.attrs.update({'class': 'form-control'})
        self.fields['escola'].widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = super().clean()
        tipo_usuario = cleaned_data.get('tipo_usuario')
        escola = cleaned_data.get('escola')
        if tipo_usuario == CustomUser.AGENTE_ADMINISTRATIVO and not escola:
            self.add_error('escola', 'Agente Administrativo deve selecionar uma escola.')
        return cleaned_data


class ResponsavelForm(forms.ModelForm):
    class Meta:
        model = Responsavel
        fields = ['cpf', 'nome', 'numero_identidade', 'celular1', 'celular2', 'email']
        widgets = {
            'cpf': forms.TextInput(attrs={'class': 'form-control'}),
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_identidade': forms.TextInput(attrs={'class': 'form-control'}),
            'celular1': forms.TextInput(attrs={'class': 'form-control'}),
            'celular2': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

CRITERIOS_CHOICES = [
    ("RENDA FAMLIAR ATÉ MEIO SALÁRIOS-MINIMO (DE R$ 660,00)", "RENDA FAMLIAR ATÉ MEIO SALÁRIOS-MINIMO (DE R$ 660,00)"),
    ("RENDA FAMLIAR ACIMA DE MEIO SALÁRIOS-MINIMO (DE R$ 660,00 Á R$ 1.320,00)", "RENDA FAMLIAR ACIMA DE MEIO SALÁRIOS-MINIMO (DE R$ 660,00 Á R$ 1.320,00)"),
    ("RENDA FAMLIAR ACIMA DE 1 ATÉ 2 SALÁRIOS-MINIMO (DE R$ 1.320,00 Á R$ 2.640,00)", "RENDA FAMLIAR ACIMA DE 1 ATÉ 2 SALÁRIOS-MINIMO (DE R$ 1.320,00 Á R$ 2.640,00)"),
    ("RENDA FAMLIAR ACIMA DE 2 ATÉ 3 SALÁRIOS-MINIMO (DE R$ 2.640,00 Á R$ 3.960,00)", "RENDA FAMLIAR ACIMA DE 2 ATÉ 3 SALÁRIOS-MINIMO (DE R$ 2.640,00 Á R$ 3.960,00)"),
    ("RENDA FAMLIAR ACIMA DE 3 ATÉ 4 SALÁRIOS-MINIMO (DE R$ 3.960,00 Á R$ 5.280,00)", "RENDA FAMLIAR ACIMA DE 3 ATÉ 4 SALÁRIOS-MINIMO (DE R$ 3.960,00 Á R$ 5.280,00)"),
    ("RENDA FAMLIAR ACIMA DE 4 ATÉ 6 SALÁRIOS-MINIMO (DE R$ 5.280,00 Á R$ 7.920,00)", "RENDA FAMLIAR ACIMA DE 4 ATÉ 6 SALÁRIOS-MINIMO (DE R$ 5.280,00 Á R$ 7.920,00)"),
    ("RENDA FAMLIAR ACIMA DE 6 ATÉ 8 SALÁRIOS-MINIMO (DE R$ 7.920,00 Á R$ 10.560,00)", "RENDA FAMLIAR ACIMA DE 6 ATÉ 8 SALÁRIOS-MINIMO (DE R$ 7.920,00 Á R$ 10.560,00)"),
    ("RENDA FAMLIAR ACIMA DE 8 ATÉ 10 SALÁRIOS-MINIMO (DE R$ 10.560,00 Á R$ 13.260,00)", "RENDA FAMLIAR ACIMA DE 8 ATÉ 10 SALÁRIOS-MINIMO (DE R$ 10.560,00 Á R$ 13.260,00)"),
    ("RENDA FAMLIAR ACIMA DE 10 SALÁRIOS-MINIMO (R$ 13.260,00)", "RENDA FAMLIAR ACIMA DE 10 SALÁRIOS-MINIMO (R$ 13.260,00)"),
    ("FAMÍLIAS MONOPARENTAIS (Refere-se a uma mãe ou um pai que vive sem cônjuge e com filhos dependentes)", "FAMÍLIAS MONOPARENTAIS (Refere-se a uma mãe ou um pai que vive sem cônjuge e com filhos dependentes)"),
    ("ATENDIMENTO EDUCACIONAL ESPECIALIZADO - AEE (Criança com deficiência, transtorno de espectro autista, altas habilidades)", "ATENDIMENTO EDUCACIONAL ESPECIALIZADO - AEE (Criança com deficiência, transtorno de espectro autista, altas habilidades)"),
    ("RISCO NUTRICIONAL - Criança que se encontra abaixo da curva de crescimento ou com laudo de desnutrição", "RISCO NUTRICIONAL - Criança que se encontra abaixo da curva de crescimento ou com laudo de desnutrição"),
    ("BONIFICAÇÃO POR TEMPO DE INSCRIÇÃO - 06 meses (5 pontos)", "BONIFICAÇÃO POR TEMPO DE INSCRIÇÃO - 06 meses (5 pontos)"),
    ("BONIFICAÇÃO POR TEMPO DE INSCRIÇÃO - 12 meses (15 pontos)", "BONIFICAÇÃO POR TEMPO DE INSCRIÇÃO - 12 meses (15 pontos)"),
    ("BONIFICAÇÃO POR TEMPO DE INSCRIÇÃO - 24 meses (25 pontos)", "BONIFICAÇÃO POR TEMPO DE INSCRIÇÃO - 24 meses (25 pontos)"),
]


class AlunoForm(forms.ModelForm):
    criterios_especiais = forms.MultipleChoiceField(
        choices=CRITERIOS_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Aluno
        fields = [
            'nome_completo', 'data_nascimento', 'cpf', 'sexo', 'tem_gemeo', 'nome_mae', 
            'responsavel_nome', 'responsavel_cpf', 'responsavel_numero_identidade', 'responsavel_celular1', 
            'responsavel_celular2', 'responsavel_email', 'necessidade_especial', 'bairro_escola', 
            'modalidade_ensino', 'serie_ano', 'primeira_escolha', 'segunda_escolha', 
            'cep', 'endereco', 'bairro', 'numero_residencia', 'complemento', 
            'criterios_especiais',
        ]
        widgets = {
            'nome_completo': forms.TextInput(attrs={'class': 'form-control'}),
            'data_nascimento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control'}),
            'sexo': forms.Select(attrs={'class': 'form-control'}),
            'tem_gemeo': forms.Select(attrs={'class': 'form-control'}),
            'nome_mae': forms.TextInput(attrs={'class': 'form-control'}),
            'responsavel_nome': forms.TextInput(attrs={'class': 'form-control'}),
            'responsavel_cpf': forms.TextInput(attrs={'class': 'form-control'}),
            'responsavel_numero_identidade': forms.TextInput(attrs={'class': 'form-control'}),
            'responsavel_celular1': forms.TextInput(attrs={'class': 'form-control'}),
            'responsavel_celular2': forms.TextInput(attrs={'class': 'form-control'}),
            'responsavel_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'necessidade_especial': forms.Select(attrs={'class': 'form-control'}),
            'bairro_escola': forms.TextInput(attrs={'class': 'form-control'}),
            'modalidade_ensino': forms.Select(attrs={'class': 'form-control'}),
            'serie_ano': forms.Select(attrs={'class': 'form-control'}),
            'primeira_escolha': forms.Select(attrs={'class': 'form-control'}),
            'segunda_escolha': forms.Select(attrs={'class': 'form-control'}),
            'cep': forms.TextInput(attrs={'class': 'form-control'}),
            'endereco': forms.TextInput(attrs={'class': 'form-control'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_residencia': forms.TextInput(attrs={'class': 'form-control'}),
            'complemento': forms.TextInput(attrs={'class': 'form-control'}),
            'criterios_especiais': forms.CheckboxSelectMultiple()  # Permitir múltiplas escolhas
        }
        error_messages = {
            'cpf': {
                'unique': "Um aluno com este CPF já está cadastrado.",
            },
        }

    def clean_responsavel_cpf(self):
        responsavel_cpf = self.cleaned_data.get('responsavel_cpf')
        if responsavel_cpf:
            # Remove pontos e traços do CPF
            responsavel_cpf = responsavel_cpf.replace('.', '').replace('-', '')
        return responsavel_cpf
    

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if cpf:
            # Remove pontos e traços do CPF
            cpf = cpf.replace('.', '').replace('-', '')
        return cpf




class AlunoPesquisaForm(forms.Form):
    MODALIDADE_CHOICES = [
        ('1', 'EDUCAÇÃO INFANTIL'),
        ('2', 'ENSINO FUNDAMENTAL'),
        # Adicione outras modalidades aqui
    ]

    SERIE_ANO_CHOICES = [
        ('1', '1º ANO'),
        ('2', '2º ANO'),
        # Adicione outras séries aqui
    ]

    FILTRO_CHOICES = [
        ('1', 'Filtro 1'),
        ('2', 'Filtro 2'),
        # Adicione outros filtros aqui
    ]

    modalidade = forms.ChoiceField(choices=MODALIDADE_CHOICES, required=True, label='Modalidade de ensino')
    serie_ano = forms.ChoiceField(choices=SERIE_ANO_CHOICES, required=True, label='Série / ano / período')
    filtro = forms.ChoiceField(choices=FILTRO_CHOICES, required=True, label='Filtro')


class EscolaForm(forms.ModelForm):
    modalidade = forms.ModelChoiceField(queryset=ModalidadeEnsino.objects.all(), required=True, label='Modalidade de Ensino')
    serie = forms.ModelChoiceField(queryset=SerieAno.objects.all(), required=True, label='Série / Ano')

    class Meta:
        model = Escola
        fields = ['nome', 'bairro', 'modalidade', 'serie', 'vagas_totais', 'vagas_disponiveis']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control'}),
            'modalidade': forms.Select(attrs={'class': 'form-control'}),
            'serie': forms.Select(attrs={'class': 'form-control'}),
            'vagas_totais': forms.NumberInput(attrs={'class': 'form-control'}),
            'vagas_disponiveis': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class ModalidadeEnsinoForm(forms.ModelForm):
    class Meta:
        model = ModalidadeEnsino
        fields = ['descricao']
        widgets = {
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),
        }

class SerieAnoForm(forms.ModelForm):
    class Meta:
        model = SerieAno
        fields = ['descricao', 'modalidade_ensino']
        widgets = {
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),
            'modalidade_ensino': forms.Select(attrs={'class': 'form-control'}),
        }