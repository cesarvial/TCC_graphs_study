# 05/09/2023
Cold start: problema no início, quando não existe uma referência para recomendação do usuário. Uma alternativa para isso poderia ser ter "caminhos padrão" dependendo nos gostos preliminares do estudante. Claro que seria mais difícil pois muitos alunos podem não saber o que fazer, mas com isso o aluno já poderia ver opções de trilha desde o início do curso.

Visualização gráfica é importante - deixar claro para o estudante qual será o "caminho" que ele terá que percorrer no curso, quais as ligações desse caminho e quais "caminhos secundários" ele pode buscar e como.

Algo importante também é não limitar o estudante - ele tem muitas opções e elas devem ser apresentadas para ele.


## Maneiras de recomendação
Recomendar matérias não é tão fácil, é preciso levar muito mais em conta do que recomendar um vídeo. Alguns trabalhos levam em conta:
- O histórico do aluno em questão:
    - Matérias de interesse do aluno com base em avaliações;
    - Matérias em que o aluno foi bem (pode ser usado tanto nota quanto presença)
- O histórico das disciplinas em si, levando em conta o histórico dos alunos antigos similares ao aluno sendo analizado.
- "Créditos". No nosso caso isso não existe dessa forma, mas pode ser levado em conta:
    - Ajudar o aluno a finalizar uma trilha;
    - Evitar que o aluno faça matérias de mais sem conexão nenhuma.
- Popularidade da disciplina como um todo

## Referências
[User-controllable personalization: A case study with SetFusion](https://repositorio.uc.cl/server/api/core/bitstreams/d236a562-a2f9-4343-b575-1f4158d2f7c7/content)

O’Donovan, J., Smyth, B., Gretarsson, B., Bostandjiev, S., Höllerer, T. (2008). PeerChooser: visual interactive recommendation. In Proceedings of the SIGCHI Conference on Human Factors in Computing Systems

[A survey of surveys on the use of visualization for interpreting machine learning models](https://journals.sagepub.com/doi/pdf/10.1177/1473871620904671)

[Goal-based Course Recommendation](https://arxiv.org/pdf/1812.10078.pdf)

[A Score Prediction Approach for Optional Course Recommendation via Cross-User-Domain Collaborative Filtering](https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=8636939)


# 11/09/2023
Pesquisa sobre métodos de ciência de dados para apresentação de dados acadêmicos para professores e coordenadores

[Análise de um professor da Universidade de Connecticut](https://www.dylanaudette.com/how-to-interpret-grade-data). Este professor mostra como ele faz as análises estatísticas das turmas dele, bem detalhado, bem interessante.

[Artigo sobre análise de estudantes com GPA >= 100](file:///C:/Users/cesar/Downloads/Statistical_Analysis_of_Factors_Affecting_Grade_Po.pdf). Achei uma análise simples, o modelo de predição foi apenas uma regressão linear dos dados coletados.

[Uso da Kappa (?) Statistics](file:///C:/Users/cesar/Downloads/217-418-1-SM.pdf). Uso de uma análise diferente.

[ADEGA PDF](https://periodicos.ufsm.br/coming/article/view/67933/pdf). Com certeza o melhor trabalho na área, mas em seu artigo/documentação só é comentado sobre as tecnologias usadas, não muito sobre a metodologia de análise de dados. Ou seja, **VER REFERÊNCIAS**. 
Algumas outras coisas legais são a exportação de dados para modelos preditivos próprios, e a importação de dados de sites como SIE. Isso seria bom ser revisado pois seu uso é interessante, mas caso isso seja feito especificamente para o sistema da UTFPR (o que eu acredito ser o caso), isso não seria muito útil.


Coisas a se notar:
- O GPA (no nosso caso seria o CR) foi levado em conta em todas as pesquisas;
- A separação entre sexos também foi algo que foi bastante levado em conta, apesar de eu não ser fã;
- 



# 12/09/2023
Reunião

- cold-start com o aluno selecionando qual o seu objetivo
- Separar os alunos em "grupos"

Sistema de recomendação de um percurso 



# 12/12/2023

file:///C:/Users/cesar/Downloads/IIITD_Course_Recommendation_System.pdf

https://arxiv.org/pdf/2101.12153.pdf

Análise exploratória - "metadados" dos nossos dados.

Criar grafos de estudantes onde a ligação são as disciplinas.