from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "chave_secreta"  # Necessária para usar sessões

# Lista de barbeiros simulando uma base de dados
barbeiros = [
    {"id": 1, "nome": "Felippe", "login": "felippe", "senha": "0956kaue"},
    {"id": 2, "nome": "João", "login": "joao", "senha": "5678"},
    {"id": 3, "nome": "Pedro", "login": "pedro", "senha": "abcd"}
]

# Lista para armazenar os agendamentos
agendamentos = []

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/agendar", methods=["GET", "POST"])
def agendar():
    if request.method == "POST":
        # Captura dos dados do formulário
        nome = request.form.get("nome", "").strip()
        telefone = request.form.get("telefone", "").strip()
        horario = request.form.get("horario", "").strip()
        barbeiro_id = request.form.get("barbeiro_id", "").strip()

        # Validação de campos obrigatórios
        if not nome or not telefone or not horario or not barbeiro_id:
            return render_template(
                "agendar.html", 
                barbeiros=barbeiros, 
                error="Todos os campos são obrigatórios."
            )

        # Verificar se já existe um agendamento para o mesmo horário e barbeiro
        for agendamento in agendamentos:
            if agendamento["horario"] == horario and agendamento["barbeiro_id"] == int(barbeiro_id):
                return render_template(
                    "agendar.html", 
                    barbeiros=barbeiros, 
                    error="Já existe um agendamento nesse horário para o mesmo barbeiro."
                )

        # Adicionar o agendamento à lista
        novo_agendamento = {
            "id": len(agendamentos) + 1,
            "nome": nome,
            "telefone": telefone,
            "horario": horario,
            "barbeiro_id": int(barbeiro_id),
            "confirmado": False
        }
        agendamentos.append(novo_agendamento)

        # Renderiza a página de confirmação
        barbeiro_nome = next(b["nome"] for b in barbeiros if b["id"] == int(barbeiro_id))
        return render_template(
            "confirmacao.html", 
            nome=nome, 
            telefone=telefone, 
            horario=horario, 
            barbeiro=barbeiro_nome
        )

    # Exibe o formulário de agendamento com a lista de barbeiros
    return render_template("agendar.html", barbeiros=barbeiros)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login = request.form.get("login")
        senha = request.form.get("senha")
        
        # Verificar login e senha
        for barbeiro in barbeiros:
            if barbeiro["login"] == login and barbeiro["senha"] == senha:
                session["logged_in"] = True
                session["barbeiro_id"] = barbeiro["id"]
                session["barbeiro_nome"] = barbeiro["nome"]
                return redirect(url_for("admin"))
        
        return render_template("login.html", error="Usuário ou senha inválidos.")
    return render_template("login.html")

@app.route("/admin")
def admin():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    
    barbeiro_id = session.get("barbeiro_id")
    barbeiro_nome = session.get("barbeiro_nome")
    
    # Filtrar agendamentos do barbeiro logado
    agendamentos_barbeiro = [ag for ag in agendamentos if ag["barbeiro_id"] == barbeiro_id]
    return render_template("admin.html", nome=barbeiro_nome, agendamentos=agendamentos_barbeiro)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/confirmar/<int:agendamento_id>", methods=["POST"])
def confirmar(agendamento_id):
    try:
        # Encontrar o agendamento pelo ID
        agendamento = next((ag for ag in agendamentos if ag["id"] == agendamento_id), None)
        if not agendamento:
            return "Erro: Agendamento não encontrado.", 400

        # Confirmar o agendamento
        agendamento["confirmado"] = True

        # Criar o link do WhatsApp
        telefone = agendamento["telefone"]
        mensagem = f"Olá {agendamento['nome']}, seu agendamento para {agendamento['horario']} foi confirmado com sucesso!"
        link_whatsapp = f"https://wa.me/55{telefone}?text={mensagem.replace(' ', '%20')}"
        return redirect(link_whatsapp)
    except Exception as e:
        print(f"Erro ao confirmar agendamento: {e}")
        return "Erro ao confirmar agendamento.", 500

if __name__ == "__main__":
    app.run(debug=True)
