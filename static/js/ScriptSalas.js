 // abrir/fechar tabela
    document.querySelectorAll('.ver-mais').forEach(botao => {
      botao.addEventListener('click', () => {
        const container = botao.nextElementSibling;
        if (container.style.display === 'none' || container.style.display === '') {
          container.style.display = 'block';
          botao.textContent = 'Ver Menos';
        } else {
          container.style.display = 'none';
          botao.textContent = 'Ver Mais';
        }
      });
    });

    // Modal
    const modal = document.getElementById("agendarModal");
    const btnCancelar = document.getElementById("cancelarModal");
    let horarioSelecionado = null;

    document.querySelectorAll('.agendar-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        horarioSelecionado = e.target.closest('tr').cells[0].textContent;
        modal.style.display = "flex";
      });
    });

    btnCancelar.addEventListener("click", () => {
      modal.style.display = "none";
    });

    // Salvar no localStorage
    document.getElementById("salvarAgendamento").addEventListener("click", () => {
      const nome = document.getElementById("nome").value.trim();
      const motivo = document.getElementById("motivo").value.trim();

      if (!nome || !motivo) {
        alert("Preencha todos os campos!");
        return;
      }

      let agendamentos = JSON.parse(localStorage.getItem("agendamentos")) || [];
      agendamentos.push({
        nome: nome,
        motivo: motivo,
        horario: horarioSelecionado,
        status: "Pendente"
      });
      localStorage.setItem("agendamentos", JSON.stringify(agendamentos));

      alert("Agendamento solicitado com sucesso!");
      modal.style.display = "none";
      document.getElementById("nome").value = "";
      document.getElementById("motivo").value = "";
    });