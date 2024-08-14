from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import CustomAuthenticationForm, CustomUserCreationForm, CustomUserLoginForm, ResponsavelForm, AlunoForm
from .models import CustomUser, Responsavel, Aluno, ResponsavelPeloAluno, NecessidadeEspecial, ModalidadeEnsino, SerieAno, Escola, Anotacao
from django.template.loader import render_to_string
from django.http import JsonResponse
from .forms import AlunoPesquisaForm
import json  # Adicione esta linha
from django.views.decorators.csrf import csrf_exempt
from weasyprint import HTML
from django.http import HttpResponse
from django.templatetags.static import static
import qrcode
import base64
from io import BytesIO
from datetime import datetime
from .forms import EscolaForm  # Certifique-se de importar o formulário corretamente
from .utils import classificar_alunos  # Import the utility function


@login_required
def atualizar_vagas(request, escola_id):
    escola = get_object_or_404(Escola, id=escola_id)
    if request.method == 'POST':
        vagas_disponiveis = int(request.POST.get('vagas_disponiveis'))
        escola.vagas_disponiveis = vagas_disponiveis
        escola.save()
        messages.success(request, 'Vagas atualizadas com sucesso!')
        return redirect('listar_escolas')
    return JsonResponse({'error': 'Método não permitido'}, status=405)


@login_required
def index(request):
    return render(request, 'index.html')

@login_required
def BASE(request):
    return render(request, 'base.html')

def login_view(request):
    if request.method == 'POST':
        form = CustomUserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            tipo_usuario = form.cleaned_data['tipo_usuario']
            escola = form.cleaned_data.get('escola')
            
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if tipo_usuario == 'AGENTE_ADMINISTRATIVO' and user.escola != escola:
                    messages.error(request, 'Você não está vinculado a esta escola.')
                else:
                    auth_login(request, user)
                    messages.success(request, f'Login realizado com sucesso! Bem-vindo(a), {user.username}!')
                    return redirect('index')
            else:
                messages.error(request, 'Nome de usuário ou senha inválidos.')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = CustomUserLoginForm()
    return render(request, 'login.html', {'form': form})


@login_required
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registro realizado com sucesso!')
            return redirect('index')
        else:
            messages.error(request, 'Houve um erro no seu registro. Por favor, tente novamente.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})



def logout_view(request):
    auth_logout(request)
    messages.success(request, 'Logout realizado com sucesso!')
    return redirect('login')

def get_user_type(request):
    username = request.GET.get('username')
    user = CustomUser.objects.filter(username=username).first()
    if user:
        return JsonResponse({'tipo_usuario': user.tipo_usuario})
    return JsonResponse({'tipo_usuario': ''})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registro realizado com sucesso!')
            return redirect('index')
        else:
            messages.error(request, 'Houve um erro no seu registro. Por favor, tente novamente.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def cadastro_responsavel(request):
    if request.method == 'POST':
        form = ResponsavelForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Responsável cadastrado com sucesso!')
            return redirect('cadastro_responsavel')
        else:
            messages.error(request, 'Erro ao cadastrar responsável.')
    else:
        form = ResponsavelForm()
    return render(request, 'alunos/cadastro_responsavel.html', {'responsavel_form': form})

@login_required
def cadastro_aluno(request):
    if request.method == 'POST':
        aluno_form = AlunoForm(request.POST)
        if aluno_form.is_valid():
            aluno = aluno_form.save(commit=False)
            aluno.responsavel_cadastro = request.user
            aluno.save()
            if aluno.em_espera:
                messages.warning(request, f'Aluno {aluno.nome_completo} cadastrado com sucesso, mas está Aguardando...!')
            else:
                messages.success(request, f'Aluno {aluno.nome_completo} cadastrado com sucesso!')
            return redirect('cadastro_aluno')
        else:
            # Se o formulário não for válido, exibe as mensagens de erro
            for error in aluno_form.errors.values():
                messages.error(request, error)
    else:
        aluno_form = AlunoForm()

    context = {
        'aluno_form': aluno_form,
    }
    return render(request, 'alunos/cadastro_aluno.html', context)




@login_required
def visualizar_alunos(request):
    alunos = Aluno.objects.all()
    return render(request, 'visualizar_alunos.html', {'alunos': alunos})

@csrf_exempt
def get_responsavel_by_cpf(request):
    cpf = request.GET.get('cpf', '')
    try:
        alunos = Aluno.objects.filter(responsavel_cpf=cpf)
        if alunos.exists():
            aluno = alunos.first()  # Obtém o primeiro aluno da lista
            data = {
                'success': True,
                'name': aluno.responsavel_nome,
                'numero_identidade': aluno.responsavel_numero_identidade,
                'celular1': aluno.responsavel_celular1,
                'celular2': aluno.responsavel_celular2,
                'email': aluno.responsavel_email,
            }
        else:
            data = {'success': False, 'message': 'CPF não encontrado.'}
    except Exception as e:
        data = {'success': False, 'message': str(e)}
    return JsonResponse(data)


# Método para limpar e formatar o CPF do responsável
def clean_responsavel_cpf(self):
    responsavel_cpf = self.cleaned_data.get('responsavel_cpf')
    if responsavel_cpf:
        responsavel_cpf = responsavel_cpf.replace('.', '').replace('-', '')  # Remove pontos e traços
    return responsavel_cpf

# Método para limpar e formatar o CPF do aluno
def clean_cpf(self):
    cpf = self.cleaned_data.get('cpf')
    if cpf:
        cpf = cpf.replace('.', '').replace('-', '')  # Remove pontos e traços
    return cpf



@login_required
def visualizar_alunos(request):
    alunos = Aluno.objects.all()
    return render(request, 'visualizar_alunos.html', {'alunos': alunos})


def pesquisar_alunos(request):
    form = AlunoPesquisaForm()
    alunos_primeira_opcao = []
    alunos_segunda_opcao = []
    
    if request.method == 'POST':
        form = AlunoPesquisaForm(request.POST)
        if form.is_valid():
            modalidade = form.cleaned_data['modalidade']
            serie_ano = form.cleaned_data['serie_ano']
            filtro = form.cleaned_data['filtro']

            # Aqui você pode adicionar os filtros desejados
            alunos_primeira_opcao = Aluno.objects.filter(modalidade=modalidade, serie_ano=serie_ano, opcao='1')
            alunos_segunda_opcao = Aluno.objects.filter(modalidade=modalidade, serie_ano=serie_ano, opcao='2')

    context = {
        'form': form,
        'alunos_primeira_opcao': alunos_primeira_opcao,
        'alunos_segunda_opcao': alunos_segunda_opcao,
    }
    return render(request, 'pesquisar_alunos.html', context)

@login_required
def visualizar_alunos(request):
    modalidades = ModalidadeEnsino.objects.all()
    series_anos = SerieAno.objects.all()

    modalidade_id = request.GET.get('modalidade')
    serie_ano_id = request.GET.get('serie_ano')
    search_query = request.GET.get('search', '')

    # Se o usuário for um agente administrativo, filtre os alunos pela escola vinculada
    if request.user.tipo_usuario == 'AGENTE_ADMINISTRATIVO':
        escola_vinculada = request.user.escola
        if escola_vinculada:
            alunos = Aluno.objects.filter(primeira_escolha=escola_vinculada)
        else:
            alunos = Aluno.objects.none()  # Se não houver escola vinculada, não mostrar alunos
    else:
        # Para outros tipos de usuário (administrador ou técnico pedagógico), mostrar todos os alunos
        alunos = Aluno.objects.all()

    # Aplicar filtros adicionais conforme selecionado
    if modalidade_id:
        alunos = alunos.filter(modalidade_ensino_id=modalidade_id)
    
    if serie_ano_id:
        alunos = alunos.filter(serie_ano_id=serie_ano_id)
    
    if search_query:
        alunos = alunos.filter(nome_completo__icontains=search_query)

    # Ordena os alunos pela pontuação em ordem decrescente
    alunos = alunos.order_by('-pontuacao')

    context = {
        'modalidades': modalidades,
        'series_anos': series_anos,
        'alunos': alunos,
        'user_name': request.user.get_full_name() or request.user.username,  # Inclui o nome do usuário no contexto
    }

    return render(request, 'visualizar_alunos.html', context)

def get_series_anos(request):
    modalidade_id = request.GET.get('modalidade_id')
    series_anos = SerieAno.objects.filter(modalidade_ensino_id=modalidade_id).values('id', 'descricao')
    return JsonResponse({'series_anos': {serie_ano['id']: serie_ano['descricao'] for serie_ano in series_anos}})


@login_required
def editar_aluno(request, aluno_id):
    aluno = get_object_or_404(Aluno, id=aluno_id)
    
    if request.method == 'POST':
        form = AlunoForm(request.POST, instance=aluno)
        if form.is_valid():
            # Limpa e formata os CPFs antes de salvar
            aluno = form.save(commit=False)
            aluno.responsavel_cpf = aluno.responsavel_cpf.replace('.', '').replace('-', '')
            aluno.cpf = aluno.cpf.replace('.', '').replace('-', '')
            aluno.save()
            
            messages.success(request, 'As alterações foram salvas com sucesso.')
            return redirect('visualizar_alunos')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = AlunoForm(instance=aluno)

    criterios = [
        "RENDA FAMLIAR ATÉ MEIO SALÁRIOS-MINIMO (DE R$ 660,00)",
        "RENDA FAMLIAR ACIMA DE MEIO SALÁRIOS-MINIMO (DE R$ 660,00 Á R$ 1.320,00)",
        "RENDA FAMLIAR ACIMA DE 1 ATÉ 2 SALÁRIOS-MINIMO (DE R$ 1.320,00 Á R$ 2.640,00)",
        "RENDA FAMLIAR ACIMA DE 2 ATÉ 3 SALÁRIOS-MINIMO (DE R$ 2.640,00 Á R$ 3.960,00)",
        "RENDA FAMLIAR ACIMA DE 3 ATÉ 4 SALÁRIOS-MINIMO (DE R$ 3.960,00 Á R$ 5.280,00)",
        "RENDA FAMLIAR ACIMA DE 4 ATÉ 6 SALÁRIOS-MINIMO (DE R$ 5.280,00 Á R$ 7.920,00)",
        "RENDA FAMLIAR ACIMA DE 6 ATÉ 8 SALÁRIOS-MINIMO (DE R$ 7.920,00 Á R$ 10.560,00)",
        "RENDA FAMLIAR ACIMA DE 8 ATÉ 10 SALÁRIOS-MINIMO (DE R$ 10.560,00 Á R$ 13.260,00)",
        "RENDA FAMLIAR ACIMA DE 10 SALÁRIOS-MINIMO (R$ 13.260,00)",
        "FAMÍLIAS MONOPARENTAIS (Refere-se a uma mãe ou um pai que vive sem cônjuge e com filhos dependentes)",
        "ATENDIMENTO EDUCACIONAL ESPECIALIZADO - AEE (Criança com deficiência, transtorno de espectro autista, altas habilidades)",
        "RISCO NUTRICIONAL - Criança que se encontra abaixo da curva de crescimento ou com laudo de desnutrição",
        "BONIFICAÇÃO POR TEMPO DE INSCRIÇÃO - 06 meses (5 pontos)",
        "BONIFICAÇÃO POR TEMPO DE INSCRIÇÃO - 12 meses (15 pontos)",
        "BONIFICAÇÃO POR TEMPO DE INSCRIÇÃO - 24 meses (25 pontos)"
    ]
    
    return render(request, 'alunos/editar_aluno.html', {
        'aluno_form': form,
        'aluno': aluno,
        'criterios': criterios,
    })


@login_required
def deletar_aluno(request, aluno_id):
    aluno = get_object_or_404(Aluno, id=aluno_id)
    if request.method == 'POST':
        aluno.delete()
        messages.success(request, 'Aluno deletado com sucesso!')
        return redirect('visualizar_alunos')
    return render(request, 'alunos/deletar_aluno.html', {'aluno': aluno})


def informacao_aluno(request, aluno_id):
    aluno = get_object_or_404(Aluno, id=aluno_id)
    return render(request, 'informacao_aluno.html', {'aluno': aluno})

@login_required
def imprimir_aluno(request, aluno_id):
    aluno = Aluno.objects.get(id=aluno_id)
    
    # Renderiza o template com os dados do aluno
    html_string = render_to_string('alunos/ficha_matricula.html', {'aluno': aluno})
    
    # Converte o HTML para PDF
    html = HTML(string=html_string)
    pdf = html.write_pdf()

    # Configura a resposta HTTP para enviar o PDF
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="ficha_matricula_{aluno.nome_completo}.pdf"'

    return response

def anotacoes_aluno(request, aluno_id):
    aluno = get_object_or_404(Aluno, id=aluno_id)
    # Lógica de anotações
    return render(request, 'anotacoes_aluno.html', {'aluno': aluno})

def visualizar_aluno(request, aluno_id):
    aluno = get_object_or_404(Aluno, id=aluno_id)
    return render(request, 'visualizar_aluno.html', {'aluno': aluno})

def salvar_anotacao(request, aluno_id):
    if request.method == 'POST':
        aluno = Aluno.objects.get(id=aluno_id)
        data_contato = request.POST.get('data_contato')
        anotacao = request.POST.get('anotacao')

        nova_anotacao = Anotacao(aluno=aluno, data_contato=data_contato, anotacao=anotacao)
        nova_anotacao.save()

        messages.success(request, 'Anotação salva com sucesso!')
        return redirect('visualizar_alunos')
    


@login_required
def salvar_observacao(request):
    if request.method == 'POST':
        aluno_id = request.POST.get('aluno_id')
        anotacao = request.POST.get('anotacao')
        data_contato = request.POST.get('data_contato')

        aluno = get_object_or_404(Aluno, id=aluno_id)

        # Converte a string de data para um objeto de data
        try:
            data_contato_obj = datetime.strptime(data_contato, '%Y-%m-%d').date()
            data_contato_formatada = data_contato_obj.strftime('%d/%m/%Y')
        except ValueError:
            data_contato_formatada = data_contato  # Se a conversão falhar, usa a string original

        # Prepara a anotação para ser salva
        nova_anotacao = f"{request.user.get_full_name() or request.user.username} ({data_contato_formatada}): {anotacao}\n"

        # Concatena a nova anotação com as anteriores
        if aluno.observacao:
            aluno.observacao += "\n" + nova_anotacao
        else:
            aluno.observacao = nova_anotacao

        aluno.save()

        messages.success(request, 'Anotação salva com sucesso!')
        return redirect('visualizar_alunos')

@login_required
def sua_view(request):
    # Carrega todas as modalidades de ensino
    modalidades_ensino = ModalidadeEnsino.objects.all()
    print(modalidades_ensino)

    
    # Carrega todas as séries/anos
    series_anos = SerieAno.objects.all()

    # Verifica se uma modalidade foi selecionada para filtrar as séries/anos
    selected_modalidade_id = request.GET.get('modalidade_ensino')
    if selected_modalidade_id:
        series_anos = series_anos.filter(modalidade_ensino_id=selected_modalidade_id)

    # Verifica se a requisição é AJAX para retornar as séries/anos como JSON
    if request.is_ajax():
        series_anos_list = [{'id': serie.id, 'descricao': serie.descricao} for serie in series_anos]
        return JsonResponse({'series_anos': series_anos_list})

    # Prepara o contexto para renderizar o template
    context = {
        'user_name': request.user.get_full_name() or request.user.username,  # Nome completo ou username do usuário logado
        'modalidades_ensino': modalidades_ensino,  # Modalidades de ensino para o template
        'series_anos': series_anos,  # Séries/Ano para o template
        'selected_modalidade_id': selected_modalidade_id,  # Modalidade selecionada, se houver
    }

    # Renderiza o template com o contexto
    return render(request, 'seu_template.html', context)

@login_required
def get_observacoes(request, aluno_id):
    aluno = get_object_or_404(Aluno, id=aluno_id)
    return JsonResponse({'observacao': aluno.observacao})



@login_required
def index(request):
    # Inicializa as variáveis
    escolas = []
    total_students = 0
    total_schools = 0
    total_users = None

    # Lógica para carregar os dados conforme o tipo de usuário
    if request.user.is_superuser:
        # Administrador: mostrar todas as escolas e contagens gerais
        escolas = Escola.objects.all()
        total_students = Aluno.objects.count()
        total_schools = Escola.objects.count()
        total_users = CustomUser.objects.count()
    elif request.user.tipo_usuario == 'TECNICO_PEDAGOGICO':
        # Técnico Pedagógico: mostrar todas as escolas, contagem de alunos e escolas
        escolas = Escola.objects.all()
        total_students = Aluno.objects.count()
        total_schools = Escola.objects.count()
    elif request.user.tipo_usuario == 'AGENTE_ADMINISTRATIVO':
        # Agente Administrativo: mostrar apenas a escola a que está vinculado e contagem de alunos nessa escola
        escolas = Escola.objects.filter(id=request.user.escola.id) if request.user.escola else []
        total_students = Aluno.objects.filter(primeira_escolha=request.user.escola).count()
        total_schools = 1  # Apenas a escola vinculada

    context = {
        'escolas': escolas,
        'total_students': total_students,
        'total_schools': total_schools,
        'total_users': total_users,
    }
    return render(request, 'index.html', context)




@login_required
def visualizar_aluno(request, aluno_id):
    aluno = get_object_or_404(Aluno, id=aluno_id)
    responsavel_cadastro = aluno.responsavel_cadastro  # Aqui buscamos quem realmente fez o cadastro

    data = {
        'responsavel_nome': responsavel_cadastro.username if responsavel_cadastro else 'N/A',  # Nome do responsável
        'aluno_cadastro_id': aluno.id,  # ID do cadastro do aluno
        'protocolo': aluno.id,  # Usando o ID do cadastro como protocolo
        'aluno_nome_completo': aluno.nome_completo,
        'aluno_data_nascimento': aluno.data_nascimento.strftime('%d/%m/%Y'),
        'aluno_nome_mae': aluno.nome_mae,
        'aluno_sexo': aluno.sexo,
        'aluno_endereco': aluno.endereco,
        'aluno_bairro': aluno.bairro,
        'aluno_cep': aluno.cep,
        'aluno_responsavel_celular1': aluno.responsavel_celular1,
        'primeira_escolha': aluno.primeira_escolha.nome if aluno.primeira_escolha else '',
        'segunda_escolha': aluno.segunda_escolha.nome if aluno.segunda_escolha else '',
        'solicitacao_encerrada': aluno.situacao,
    }

    return JsonResponse(data)


@login_required
def visualizar_series(request):
    selected_modalidade_id = request.GET.get('modalidade_ensino')
    
    if selected_modalidade_id:
        series_anos = SerieAno.objects.filter(modalidade_ensino_id=selected_modalidade_id)
        series_anos_list = [{'id': serie.id, 'descricao': serie.descricao} for serie in series_anos]
        return JsonResponse({'series_anos': series_anos_list})

    return JsonResponse({'error': 'Nenhuma modalidade selecionada'}, status=400)



@login_required
def gerar_pdf_aluno(request, aluno_id):
    aluno = Aluno.objects.get(id=aluno_id)
    responsavel_cadastro = aluno.responsavel_cadastro

    # Gerar o QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr_data = f"http://example.com/confirmacao/{aluno.id}"  # Substitua pela URL que deseja
    qr.add_data(qr_data)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')
    buffer = BytesIO()
    img.save(buffer)
    img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')

    # Gera o caminho completo da logo
    logo_url = request.build_absolute_uri(static('assets/dist/img/logo.png'))

    # Dados para o template
    context = {
        'logo_url': logo_url,
        'responsavel_nome': responsavel_cadastro.username if responsavel_cadastro else 'N/A',
        'aluno_cadastro_id': aluno.id,
        'protocolo': aluno.id,
        'aluno_nome_completo': aluno.nome_completo,
        'aluno_data_nascimento': aluno.data_nascimento.strftime('%d/%m/%Y'),
        'aluno_nome_mae': aluno.nome_mae,
        'aluno_sexo': aluno.sexo,
        'aluno_endereco': aluno.endereco,
        'aluno_bairro': aluno.bairro,
        'aluno_cep': aluno.cep,
        'aluno_responsavel_celular1': aluno.responsavel_celular1,
        'primeira_escolha': aluno.primeira_escolha.nome if aluno.primeira_escolha else '',
        'segunda_escolha': aluno.segunda_escolha.nome if aluno.segunda_escolha else '',
        'solicitacao_encerrada': aluno.situacao,
        'qr_code_img': img_str,  # Adiciona o QR code ao contexto, já codificado em Base64
    }
    
    # Renderiza o template com os dados do aluno
    html_string = render_to_string('alunos/ficha_matricula.html', context)
    
    # Converte o HTML para PDF
    html = HTML(string=html_string)
    pdf = html.write_pdf()

    # Define o cabeçalho para visualização ou download
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="ficha_matricula_{aluno.nome_completo}.pdf"'

    return response



@login_required
def cadastro_escola(request):
    if request.method == 'POST':
        form = EscolaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Escola cadastrada com sucesso!')
            return redirect('index')
        else:
            messages.error(request, 'Erro ao cadastrar a escola.')
    else:
        form = EscolaForm()
    return render(request, 'cadastro_escola.html', {'form': form})


@login_required
def remanejar_aluno(request, aluno_id):
    aluno = get_object_or_404(Aluno, id=aluno_id)
    if request.method == 'POST':
        nova_escola_id = request.POST.get('nova_escola')
        nova_escola = get_object_or_404(Escola, id=nova_escola_id)

        # Atualiza a escola do aluno
        aluno.primeira_escolha = nova_escola
        aluno.save()

        messages.success(request, 'Aluno remanejado com sucesso!')
        return redirect('visualizar_alunos')

    escolas = Escola.objects.all()
    return render(request, 'remanejar_aluno.html', {'aluno': aluno, 'escolas': escolas})


def listar_escolas(request):
    if request.user.tipo_usuario == "ADMINISTRADOR" or request.user.tipo_usuario == "TECNICO_PEDAGOGICO":
        escolas = Escola.objects.all()
    else:
        escolas = Escola.objects.filter(id=request.user.escola_id)
    
    return render(request, 'listar_escolas.html', {'escolas': escolas})



@login_required
def editar_escola(request, escola_id):
    escola = get_object_or_404(Escola, id=escola_id)
    if request.method == 'POST':
        form = EscolaForm(request.POST, instance=escola)
        if form.is_valid():
            form.save()
            messages.success(request, 'Escola atualizada com sucesso!')
            return redirect('listar_escolas')
    else:
        form = EscolaForm(instance=escola)
    return render(request, 'editar_escola.html', {'form': form, 'escola': escola})


@login_required
def alterar_situacao_apto(request, aluno_id):
    aluno = get_object_or_404(Aluno, id=aluno_id)
    if request.method == 'POST':
        aluno.situacao = 'ALUNO APTO'
        aluno.save()
        messages.success(request, f'Situação do aluno {aluno.nome_completo} alterada para APTO com sucesso.')
        return redirect('visualizar_alunos')
    else:
        messages.error(request, 'Método de requisição inválido.')
        return redirect('visualizar_alunos')
