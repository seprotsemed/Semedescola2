from django.contrib import admin
from django.urls import path
from webapp import views
from .views import get_observacoes
from .views import gerar_pdf_aluno
from .views import listar_escolas, editar_escola
from .views import atualizar_vagas
from .views import alterar_situacao_apto

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('base/', views.BASE, name='base'),
    path('get-user-type/', views.get_user_type, name='get_user_type'),
    path('cadastro_responsavel/', views.cadastro_responsavel, name='cadastro_responsavel'),
    path('cadastro_aluno/', views.cadastro_aluno, name='cadastro_aluno'),
    path('visualizar_alunos/', views.visualizar_alunos, name='visualizar_alunos'),
    path('visualizar_series/', views.visualizar_series, name='visualizar_series'),
    path('get_responsavel_by_cpf/', views.get_responsavel_by_cpf, name='get_responsavel_by_cpf'),
    path('pesquisar_alunos/', views.pesquisar_alunos, name='pesquisar_alunos'),
    path('get_series_anos/', views.get_series_anos, name='get_series_anos'),
    path('editar_aluno/<int:aluno_id>/', views.editar_aluno, name='editar_aluno'),
    path('deletar_aluno/<int:aluno_id>/', views.deletar_aluno, name='deletar_aluno'),
    path('informacao_aluno/<int:aluno_id>/', views.informacao_aluno, name='informacao_aluno'),
    # path('imprimir_aluno/<int:aluno_id>/', views.imprimir_aluno, name='imprimir_aluno'),
    path('imprimir_aluno/<int:aluno_id>/', gerar_pdf_aluno, name='imprimir_aluno'),
    path('anotacoes_aluno/<int:aluno_id>/', views.anotacoes_aluno, name='anotacoes_aluno'),
    path('visualizar_aluno/<int:aluno_id>/', views.visualizar_aluno, name='visualizar_aluno'),
    path('salvar_anotacao/<int:aluno_id>/', views.salvar_anotacao, name='salvar_anotacao'),
    path('salvar_observacao/', views.salvar_observacao, name='salvar_observacao'),
    path('get_observacoes/<int:aluno_id>/', get_observacoes, name='get_observacoes'),
    path('cadastro_escola/', views.cadastro_escola, name='cadastro_escola'),
    path('listar_escolas/', listar_escolas, name='listar_escolas'),path('aluno/<int:aluno_id>/alterar-situacao-apto/', alterar_situacao_apto, name='alterar_situacao_apto'),
    path('editar_escola/<int:escola_id>/', editar_escola, name='editar_escola'),  # View de edição
    path('atualizar_vagas/<int:escola_id>/', atualizar_vagas, name='atualizar_vagas'),
    path('aluno/<int:aluno_id>/alterar-situacao-apto/', alterar_situacao_apto, name='alterar_situacao_apto'),
    path('alunos_apto/', views.alunos_apto, name='alunos_apto'),
    path('informacao_aluno_apto/<int:aluno_id>/', views.informacao_aluno_apto, name='informacao_aluno_apto'),
    path('gerar_pdf_alunos_aptos/', views.gerar_pdf_alunos_aptos, name='gerar_pdf_alunos_aptos'),
]
