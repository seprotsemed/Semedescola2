from .models import Aluno

def classificar_alunos(escola):
    """
    This function updates the classification of students based on the available spots in the school.
    If there are spots available, students are classified as 'Classificado'.
    """
    # Get all students in the order list, ordered by their score (pontuacao)
    alunos = Aluno.objects.filter(primeira_escolha=escola).order_by('ordenacao')

    # Initialize a counter for available spots
    vagas = escola.vagas_disponiveis

    for aluno in alunos:
        if vagas > 0:
            aluno.classificacao = 'Classificado'
            vagas -= 1  # Decrease available spots
        else:
            aluno.classificacao = 'Em Espera'
        aluno.save()  # Save the updated classification for each student

    # Update the number of available spots in the school
    escola.vagas_disponiveis = vagas
    escola.save()
