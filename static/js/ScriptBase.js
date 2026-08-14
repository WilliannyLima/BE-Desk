// ScriptBase.js

// Importante: No Django, você usará views e templates para gerar o HTML inicial,
// e o servidor fará o trabalho de manipulação de dados e status de agendamento.
// Este script manterá apenas a interatividade da interface (modais, tabs, dropdown).

// FUNÇÃO JS ADICIONADA: Controla a exibição do dropdown ao clicar
function toggleDropdown() {
    const dropdownContent = document.querySelector('#agendamentosDropdown .dropdown-content');
    // Alterna a classe 'show' (dependendo do seu CSS) ou alterna a propriedade 'display'
    dropdownContent.style.display = dropdownContent.style.display === 'block' ? 'none' : 'block';
}

// --- CÓDIGO JS MANTIDO PARA INTERAÇÃO DO USUÁRIO (DOM/UI) ---

// Elementos do DOM (mantidos)
const bookingModal = document.getElementById("bookingModal");
const detailsModal = document.getElementById("detailsModal");
// Removido: bookingForm (a submissão será gerenciada pelo Django)
// Removido: myBookingsList, pendingBookingsList, detailsContent, acceptButton (O Django preencherá estes conteúdos com dados reais)

// Removido: bookings, timeSlots, daysOfWeek, renderScheduleTable, renderMyBookingsList, renderPendingBookingsList, showDetails, acceptBooking, addSlotClickListeners

// Função para troca de abas (Mantida, pois é pura manipulação de CSS/DOM)
function showTab(button, tabId) {
    document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    button.classList.add('active');
    document.getElementById(`${tabId}-tab`).classList.add('active');

    // Fechar dropdown ao clicar em uma aba
    document.querySelector('#agendamentosDropdown .dropdown-content').style.display = 'none';

    // *** NOTA: REMOVEMOS 'renderAllTabs()'. O CONTEÚDO SERÁ CARREGADO POR VIEWS DO DJANGO, NÃO POR JS. ***
}

// Lógica para ABRIR o Modal de Agendamento (Adaptada)
// Se você está usando o Django, o link de agendamento deve apontar para a sua view ou 
// você precisa re-escrever essa lógica para apenas mostrar o modal quando o clique ocorrer.
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.empty-slot').forEach(cell => {
        cell.addEventListener('click', () => {
            // Em uma aplicação Django real, o modal de agendamento pode precisar
            // do 'day' e 'time' para pré-selecionar campos ou como dados ocultos.
            // Aqui, apenas mostramos o modal:
            bookingModal.style.display = "block";
            
            // Removido: currentBookingDay = cell.dataset.day; e currentBookingTime = cell.dataset.time; 
            // Estes valores seriam passados como campos HIDDEN no formulário Django.
        });
    });
});


// Lógica dos modais (Fechar - Mantida)
document.querySelectorAll('.close-button').forEach(btn => {
    btn.addEventListener('click', () => {
        bookingModal.style.display = "none";
        detailsModal.style.display = "none";
    });
});

window.addEventListener('click', (event) => {
    if (event.target == bookingModal) {
        bookingModal.style.display = "none";
    }
    if (event.target == detailsModal) {
        detailsModal.style.display = "none";
    }
    // Lógica para fechar dropdown ao clicar fora
    if (!event.target.closest('.dropdown')) {
        const dropdownContent = document.querySelector('#agendamentosDropdown .dropdown-content');
        if (dropdownContent) {
            dropdownContent.style.display = 'none';
        }
    }
});


// Lógica de Inicialização (Mantida)
document.addEventListener('DOMContentLoaded', () => {
    // *** NÃO PRECISA MAIS CHAMAR renderAllTabs() AQUI. O DJANGO JÁ GERA O HTML COMPLETO. ***
    
    // Lógica para verificar usuário logado e esconder botões (Se depender apenas de localStorage, mantenha)
    const loggedUser = localStorage.getItem("userLogged");
    if (loggedUser) {
        const headerButtons = document.querySelector(".header-buttons");
        if (headerButtons) {
            headerButtons.style.display = "none"; 
        }
    }

    // Código sugerido para reabrir o modal em caso de erro de validação do Django
    if (document.querySelector('#bookingModal .errorlist, #bookingModal .error')) {
        bookingModal.style.display = 'block';
    }
});