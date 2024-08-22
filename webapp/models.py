from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User


class ModalidadeEnsino(models.Model):
    descricao = models.CharField(max_length=255)

    def __str__(self):
        return self.descricao

class SerieAno(models.Model):
    descricao = models.CharField(max_length=255)
    modalidade_ensino = models.ForeignKey(ModalidadeEnsino, on_delete=models.CASCADE, related_name='series_anos')

    def __str__(self):
        return self.descricao


class Escola(models.Model):
    nome = models.CharField(max_length=100)
    bairro = models.CharField(max_length=100)
    modalidade = models.ForeignKey(ModalidadeEnsino, on_delete=models.CASCADE)
    serie = models.ForeignKey(SerieAno, on_delete=models.CASCADE)
    vagas_totais = models.IntegerField()  # Campo para total de vagas
    vagas_disponiveis = models.IntegerField(default=0)

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        # Verifica se a escola já existe
        if self.pk:
            old_escola = Escola.objects.get(pk=self.pk)
            # Calcula a diferença de vagas disponíveis antes da atualização
            vagas_diff = self.vagas_disponiveis - old_escola.vagas_disponiveis

            # Se houver aumento nas vagas disponíveis, atualiza a classificação dos alunos
            if vagas_diff > 0:
                self.update_classificacao(vagas_diff)

            # Ajusta as vagas totais para incluir as novas vagas adicionadas
            self.vagas_totais += vagas_diff
        else:
            vagas_diff = self.vagas_disponiveis

        # Salva a escola
        super().save(*args, **kwargs)

        # Após salvar, se houver novas vagas, ajuste a quantidade de vagas disponíveis para 0
        if vagas_diff > 0:
            self.vagas_disponiveis = 0
            super().save(update_fields=['vagas_disponiveis'])

    def update_classificacao(self, vagas_diff):
        # Obtém os alunos em espera para esta escola ordenados por 'ordenacao'
        alunos_espera = Aluno.objects.filter(primeira_escolha=self, em_espera=True).order_by('ordenacao')

        # Atualiza a classificação dos alunos de acordo com as vagas disponíveis
        for aluno in alunos_espera[:vagas_diff]:
            aluno.classificacao = "Classificado"
            aluno.situacao = "Aguardando..."  # Situação permanece como "Aguardando..."
            aluno.em_espera = False
            aluno.save()

        # Atualiza o número de vagas disponíveis
        self.vagas_disponiveis -= min(vagas_diff, len(alunos_espera))
        super().save(update_fields=['vagas_disponiveis'])


class CustomUser(AbstractUser):
    ADMINISTRADOR = 'ADMINISTRADOR'
    TECNICO_PEDAGOGICO = 'TECNICO_PEDAGOGICO'
    AGENTE_ADMINISTRATIVO = 'AGENTE_ADMINISTRATIVO'

    TIPO_USUARIO_CHOICES = [
        (ADMINISTRADOR, 'Administrador'),
        (TECNICO_PEDAGOGICO, 'Técnico Pedagógico'),
        (AGENTE_ADMINISTRATIVO, 'Agente Administrativo'),
    ]

    tipo_usuario = models.CharField(max_length=25, choices=TIPO_USUARIO_CHOICES, default=AGENTE_ADMINISTRATIVO)
    escola = models.ForeignKey(Escola, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.username

class Responsavel(models.Model):
    cpf = models.CharField(max_length=14)
    nome = models.CharField(max_length=100)
    numero_identidade = models.CharField(max_length=20)
    celular1 = models.CharField(max_length=15)
    celular2 = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.nome

class ResponsavelPeloAluno(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

class NecessidadeEspecial(models.Model):
    descricao = models.CharField(max_length=100)

    def __str__(self):
        return self.descricao


class CriteriosEspeciais(models.Model):
    descricao = models.CharField(max_length=255)

    def __str__(self):
        return self.descricao

class Aluno(models.Model):
    nome_completo = models.CharField(max_length=255)
    data_nascimento = models.DateField()
    cpf = models.CharField(max_length=14, unique=True)
    responsavel_cadastro = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='cadastros_realizados'
    )

    STATUS_CHOICES = [
    ('ativo', 'Ativo'),
    ('inativo', 'Inativo'),
]

    status = models.CharField(max_length=7, choices=STATUS_CHOICES, default='ativo')



    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
    ]
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    tem_gemeo = models.CharField(max_length=1, choices=[('S', 'Sim'), ('N', 'Não')])
    nome_mae = models.CharField(max_length=255)
    responsavel_nome = models.CharField(max_length=100)
    responsavel_cpf = models.CharField(max_length=14, unique=False)
    responsavel_numero_identidade = models.CharField(max_length=20)
    responsavel_celular1 = models.CharField(max_length=15)
    responsavel_celular2 = models.CharField(max_length=15, blank=True, null=True)
    responsavel_email = models.EmailField(blank=True, null=True)
    necessidade_especial = models.ForeignKey(NecessidadeEspecial, on_delete=models.SET_NULL, null=True, blank=True)
    bairro_escola = models.CharField(max_length=255)
    modalidade_ensino = models.ForeignKey(ModalidadeEnsino, on_delete=models.SET_NULL, null=True, blank=True)
    serie_ano = models.ForeignKey(SerieAno, on_delete=models.SET_NULL, null=True, blank=True)
    primeira_escolha = models.ForeignKey('Escola', related_name='primeira_escolha', on_delete=models.SET_NULL, null=True, blank=True)
    segunda_escolha = models.ForeignKey('Escola', related_name='segunda_escolha', on_delete=models.SET_NULL, null=True, blank=True)
    cep = models.CharField(max_length=10)
    endereco = models.CharField(max_length=255)
    bairro = models.CharField(max_length=255)
    numero_residencia = models.CharField(max_length=10)
    complemento = models.CharField(max_length=255, blank=True, null=True)
    criterios_especiais = models.JSONField(default=list)
    data_cadastro = models.DateField(auto_now_add=True)
    hora_cadastro = models.TimeField(auto_now_add=True)

    pontuacao = models.IntegerField(null=True, blank=True)
    ordenacao = models.IntegerField(null=True, blank=True)
    situacao = models.CharField(max_length=100, null=True, blank=True)
    em_espera = models.BooleanField(default=False)
    classificacao = models.CharField(max_length=50, null=True, blank=True)
    observacao = models.TextField(null=True, blank=True)

    criterios_especiais = models.JSONField(default=list)  # ou JSONField para versões anteriores


    criterios_pontuacao = {
        "RENDA FAMLIAR ATÉ MEIO SALÁRIOS-MINIMO (DE R$ 660,00)": 45,
        "RENDA FAMLIAR ACIMA DE MEIO SALÁRIOS-MINIMO (DE R$ 660,00 Á R$ 1.320,00)": 40,
        "RENDA FAMLIAR ACIMA DE 1 ATÉ 2 SALÁRIOS-MINIMO (DE R$ 1.320,00 Á R$ 2.640,00)": 35,
        "RENDA FAMLIAR ACIMA DE 2 ATÉ 3 SALÁRIOS-MINIMO (DE R$ 2.640,00 Á R$ 3.960,00)": 30,
        "RENDA FAMLIAR ACIMA DE 3 ATÉ 4 SALÁRIOS-MINIMO (DE R$ 3.960,00 Á R$ 5.280,00)": 25,
        "RENDA FAMLIAR ACIMA DE 4 ATÉ 6 SALÁRIOS-MINIMO (DE R$ 5.280,00 Á R$ 7.920,00)": 20,
        "RENDA FAMLIAR ACIMA DE 6 ATÉ 8 SALÁRIOS-MINIMO (DE R$ 7.920,00 Á R$ 10.560,00)": 15,
        "RENDA FAMLIAR ACIMA DE 8 ATÉ 10 SALÁRIOS-MINIMO (DE R$ 10.560,00 Á R$ 13.260,00)": 10,
        "RENDA FAMLIAR ACIMA DE 10 SALÁRIOS-MINIMO (R$ 13.260,00)": 5,
        "FAMÍLIAS MONOPARENTAIS (Refere-se a uma mãe ou um pai que vive sem cônjuge e com filhos dependentes)": 25,
        "ATENDIMENTO EDUCACIONAL ESPECIALIZADO - AEE (Criança com deficiência, transtorno de espectro autista, altas habilidades)": 25,
        "RISCO NUTRICIONAL - Criança que se encontra abaixo da curva de crescimento ou com laudo de desnutrição": 25,
        "BONIFICAÇÃO POR TEMPO DE INSCRIÇÃO - 06 meses (5 pontos)": 5,
        "BONIFICAÇÃO POR TEMPO DE INSCRIÇÃO - 12 meses (15 pontos)": 15,
        "BONIFICAÇÃO POR TEMPO DE INSCRIÇÃO - 24 meses (25 pontos)": 25,
    }


    def calcular_pontuacao(self):
        pontuacao = 0
        for criterio in self.criterios_especiais:
            pontuacao += self.criterios_pontuacao.get(criterio, 0)
        return pontuacao

    def save(self, *args, **kwargs):
        # Calcula a pontuação
        self.pontuacao = self.calcular_pontuacao()

        # Verifica a disponibilidade de vagas e ajusta a classificação e situação
        if self.pk is None:  # Novo aluno
            if self.primeira_escolha and self.primeira_escolha.vagas_disponiveis > 0:
                self.primeira_escolha.vagas_disponiveis -= 1
                self.primeira_escolha.save()
                self.em_espera = False
                self.classificacao = "Classificado"
                self.situacao = "Aguardando..."
            else:
                self.em_espera = True
                self.classificacao = "Aguardando..."
                self.situacao = "Aguardando..."
        else:  # Aluno existente sendo atualizado
            old_aluno = Aluno.objects.get(pk=self.pk)
            if old_aluno.primeira_escolha != self.primeira_escolha:
                # Retorna a vaga na escola antiga
                if old_aluno.primeira_escolha:
                    old_aluno.primeira_escolha.vagas_disponiveis += 1
                    old_aluno.primeira_escolha.save()
                # Retira uma vaga na nova escola
                if self.primeira_escolha and self.primeira_escolha.vagas_disponiveis > 0:
                    self.primeira_escolha.vagas_disponiveis -= 1
                    self.primeira_escolha.save()
                    self.em_espera = False
                    self.classificacao = "Classificado"
                    self.situacao = "Aguardando..."
                else:
                    self.em_espera = True
                    self.classificacao = "Aguardando..."
                    self.situacao = "Aguardando..."
        
        # Finalmente, salva o objeto
        super().save(*args, **kwargs)

class Anotacao(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE)
    tecnico = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    data_contato = models.DateField()
    anotacao = models.TextField()

    def __str__(self):
        return f"Anotação para {self.aluno.nome_completo} em {self.data_contato}"


def classificar_alunos(escola):
    alunos = Aluno.objects.filter(primeira_escolha=escola).order_by('pontuacao')
    vagas_disponiveis = escola.vagas_disponiveis

    for i, aluno in enumerate(alunos):
        if i < vagas_disponiveis:
            aluno.classificacao = "Classificado"
            aluno.situacao = "Cadastrado"
        else:
            aluno.classificacao = "Aguardando..."
            aluno.situacao = "Em Reserva"
        aluno.save()


