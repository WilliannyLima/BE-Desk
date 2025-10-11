// ScriptBase.js
        // FUNÇÃO JS ADICIONADA: Controla a exibição do dropdown ao clicar
        function toggleDropdown() {
            const dropdownContent = document.querySelector('#agendamentosDropdown .dropdown-content');
            dropdownContent.style.display = dropdownContent.style.display === 'block' ? 'none' : 'block';
        }

        // --- CÓDIGO JAVASCRIPT EXISTENTE (MANTIDO) ---

        // Dados do agendamento (simula um banco de dados)
        let bookings = [
            { id: 1, day: 'Segunda', time: '07:00 às 07:45', name: 'João', sport: 'Musculação', reason: 'Treino diário', status: 'aprovado' },
            { id: 2, day: 'Quarta', time: '07:00 às 07:45', name: 'Maria', sport: 'Natação', reason: 'Aula de natação', status: 'aprovado' },
            { id: 3, day: 'Terça', time: '09:35 às 10:20', name: 'Carlos', sport: 'Futebol', reason: 'Treino com a equipe', status: 'aprovado' },
            { id: 4, day: 'Quinta', time: '09:35 às 10:20', name: 'Ana', sport: 'Pilates', reason: 'Fisioterapia', status: 'aprovado' },
            { id: 5, day: 'Segunda', time: '10:30 às 11:15', name: 'Lucas', sport: 'Crossfit', reason: 'Treino de alta intensidade', status: 'aprovado' },
            { id: 6, day: 'Quinta', time: '10:30 às 11:15', name: 'Mariana', sport: 'Yoga', reason: 'Relaxamento e flexibilidade', status: 'aprovado' },
            { id: 7, day: 'Terça', time: '13:00 às 13:45', name: 'Pedro', sport: 'Basquete', reason: 'Jogo com amigos', status: 'aprovado' },
            { id: 8, day: 'Sexta', time: '13:00 às 13:45', name: 'Clara', sport: 'Dança', reason: 'Aula de dança', status: 'aprovado' },
            { id: 9, day: 'Quarta', time: '15:35 às 16:20', name: 'Roberto', sport: 'Vôlei', reason: 'Treino de voleibol', status: 'aprovado' },
            { id: 10, day: 'Segunda', time: '16:30 às 17:15', name: 'Fernanda', sport: 'Ginástica', reason: 'Preparação física', status: 'aprovado' },
            { id: 11, day: 'Sexta', time: '16:30 às 17:15', name: 'Paulo', sport: 'Boxe', reason: 'Aula de boxe', status: 'aprovado' },
        ];
        
        let lastBookingId = 11;
        let loggedInUser  = null; // Simula o nome do usuário logado

        // Mapeamento de horários e dias
        const timeSlots = ['07:00 às 07:45', '09:35 às 10:20', '10:30 às 11:15', '13:00 às 13:45', '15:35 às 16:20', '16:30 às 17:15', '17:15 às 18:00'];
        const daysOfWeek = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta'];

        // Elementos do DOM
        const bookingModal = document.getElementById("bookingModal");
        const detailsModal = document.getElementById("detailsModal");
        const bookingForm = document.getElementById("bookingForm");
        const myBookingsList = document.getElementById("myBookingsList");
        const pendingBookingsList = document.getElementById("pendingBookingsList");
        const detailsContent = document.getElementById('detailsContent');
        const acceptButton = document.getElementById('acceptButton');
        let currentBookingDay = '';
        let currentBookingTime = '';

        // Funções de renderização
        function renderScheduleTable() {
            const tableContainer = document.getElementById('scheduleTableContainer');
            let tableHTML = '<table><thead><tr><th>Horário</th>';
            daysOfWeek.forEach(day => tableHTML += `<th>${day}</th>`);
            tableHTML += '</tr></thead><tbody>';

            timeSlots.forEach(time => {
                tableHTML += `<tr><td>${time}</td>`;
                daysOfWeek.forEach(day => {
                    const foundBooking = bookings.find(b => b.day === day && b.time === time && b.status === 'aprovado');
                    if (foundBooking) {
                        tableHTML += `<td>${foundBooking.name}<br>${foundBooking.sport}</td>`;
                    } else {
                        tableHTML += `<td class="empty-slot" data-day="${day}" data-time="${time}">---- <i class="fa-solid fa-plus-circle"></i></td>`;
                    }
                });
                tableHTML += '</tr>';
            });

            tableHTML += '</tbody></table>';
            tableContainer.innerHTML = tableHTML;
            addSlotClickListeners();
        }

        function renderMyBookingsList() {
            const userBookings = bookings.filter(b => b.name === loggedInUser );
            if (userBookings.length === 0) {
                 myBookingsList.innerHTML = '<p style="color: black; font-weight: bold; text-align: center;">Você ainda não fez nenhum agendamento.</p>';
            } else {
                myBookingsList.innerHTML = '';
                userBookings.forEach(booking => {
                    const statusClass = booking.status === 'aprovado' ? 'status-approved' : 'status-pending';
                    const listItem = document.createElement('li');
                    listItem.innerHTML = `
                        <strong>${booking.day} - ${booking.time}</strong>
                        <span class="${statusClass}">${booking.status}</span>
                        <br>
                        Esporte: ${booking.sport}
                    `;
                    listItem.addEventListener('click', () => showDetails(booking, false));
                    myBookingsList.appendChild(listItem);
                });
            }
        }

        function renderPendingBookingsList() {
            const pendingBookings = bookings.filter(b => b.status === 'pendente');
            if (pendingBookings.length === 0) {
                pendingBookingsList.innerHTML = '<p style="color: black; font-weight: bold; text-align: center;">Não há solicitações pendentes.</p>';
            } else {
                pendingBookingsList.innerHTML = '';
                pendingBookings.forEach(booking => {
                    const listItem = document.createElement('li');
                    listItem.innerHTML = `
                        <strong>${booking.name}</strong> - ${booking.sport}
                        <span class="status-pending">Pendente</span>
                        <br>
                        Dia: ${booking.day} - Horário: ${booking.time}
                    `;
                    listItem.addEventListener('click', () => showDetails(booking, true));
                    pendingBookingsList.appendChild(listItem);
                });
            }
        }

        function showDetails(booking, isAdminView) {
            detailsContent.innerHTML = `
                <p><strong>Nome:</strong> ${booking.name}</p>
                <p><strong>Esporte:</strong> ${booking.sport}</p>
                <p><strong>Dia:</strong> ${booking.day}</p>
                <p><strong>Horário:</strong> ${booking.time}</p>
                <p><strong>Motivo:</strong> ${booking.reason}</p>
                <p><strong>Status:</strong> <span class="${booking.status === 'aprovado' ? 'status-approved' : 'status-pending'}">${booking.status}</span></p>
            `;
            
            if (isAdminView && booking.status === 'pendente') {
                acceptButton.style.display = 'block';
                acceptButton.onclick = () => acceptBooking(booking.id);
            } else {
                acceptButton.style.display = 'none';
            }

            detailsModal.style.display = "block";
        }

        function acceptBooking(bookingId) {
            const booking = bookings.find(b => b.id === bookingId);
            if (booking) {
                booking.status = 'aprovado';
                alert('Solicitação de ' + booking.name + ' aprovada!');
                detailsModal.style.display = 'none';
                renderAllTabs();
            }
        }

        function addSlotClickListeners() {
            document.querySelectorAll('.empty-slot').forEach(cell => {
                cell.addEventListener('click', () => {
                    // if (!loggedInUser ) {
                    //     alert("Você precisa fazer login para agendar um horário.");
                    //     return;
                    // }
                    currentBookingDay = cell.dataset.day;
                    currentBookingTime = cell.dataset.time;
                    bookingModal.style.display = "block";
                });
            });
        }

        function showTab(button, tabId) {
            document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            
            button.classList.add('active');
            document.getElementById(`${tabId}-tab`).classList.add('active');

            renderAllTabs();
            // Fecha o dropdown ao clicar em uma aba, se estiver aberto
            document.querySelector('#agendamentosDropdown .dropdown-content').style.display = 'none';
        }
        
        function renderAllTabs() {
            renderScheduleTable();
            renderMyBookingsList();
            renderPendingBookingsList();
        }

        // Lógica de agendamento
        bookingForm.addEventListener('submit', (event) => {
            event.preventDefault();

            if (!loggedInUser ) {
                loggedInUser  = document.getElementById("personName").value;
            }

            const newBooking = {
                id: ++lastBookingId,
                day: currentBookingDay,
                time: currentBookingTime,
                name: document.getElementById("personName").value,
                sport: document.getElementById("sport").value,
                reason: document.getElementById("reason").value,
                status: 'pendente'
            };

            bookings.push(newBooking);
            bookingModal.style.display = "none";
            bookingForm.reset();
            renderAllTabs();
            alert('Sua solicitação foi enviada e está pendente de aprovação.');
            // Muda para a aba "Meus Agendamentos" após o envio
            document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            document.querySelector('.tabs button:nth-child(2)').classList.add('active');
            document.getElementById('meus-agendamentos-tab').classList.add('active');
        });

        // Lógica dos modais
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
                document.querySelector('#agendamentosDropdown .dropdown-content').style.display = 'none';
            }
        });

        // Inicialização
        document.addEventListener('DOMContentLoaded', () => {
            renderAllTabs();
            
            // Verifica se o usuário está logado e esconde os botões (Lógica original mantida)
            const loggedUser  = localStorage.getItem("userLogged");
            if (loggedUser ) {
                const headerButtons = document.querySelector(".header-buttons");
                if (headerButtons) {
                    headerButtons.style.display = "none"; 
                }
            }
        });