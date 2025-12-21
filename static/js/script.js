// Функция для показа уведомлений
function showToast(message, category = 'info') {
    const toastContainer = document.getElementById('toast-container');

    // Определяем заголовок и цвет фона в зависимости от категории
    let title = 'Информация';
    let bgColorClass = 'bg-toast-info';

    if (category === 'success') {
        title = 'Успешно';
        bgColorClass = 'bg-toast-success';
    } else if (category === 'error') {
        title = 'Ошибка';
        bgColorClass = 'bg-toast-error';
    } else if (category === 'warning') {
        title = 'Предупреждение';
        bgColorClass = 'bg-toast-warning';
    }

    // Создаем элемент тоста
    const toastEl = document.createElement('div');
    toastEl.className = `toast ${bgColorClass}`;
    toastEl.setAttribute('role', 'alert');
    toastEl.innerHTML = `
        <div class="toast-header">
            <strong class="me-auto">${title}</strong>
            <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Закрыть"></button>
        </div>
        <div class="toast-body">
            ${message}
        </div>
    `;

    toastContainer.appendChild(toastEl);

    // Инициализируем Bootstrap Toast
    const bsToast = new bootstrap.Toast(toastEl, { delay: 3000 });
    bsToast.show();

    // Удаляем элемент из DOM после закрытия
    toastEl.addEventListener('hidden.bs.toast', () => {
        toastEl.remove();
    });
}

// Additional script for plant detail page
document.addEventListener('DOMContentLoaded', function() {
    const eventTypeSelect = document.getElementById('event_type');
    const phaseField = document.getElementById('phase_field');
    const fertilizationFields = document.getElementById('fertilization_fields');
    const phaseSelect = document.getElementById('phase_id');
    
    // Load growth phases from API
    fetch('/api/growth_phases')
        .then(response => response.json())
        .then(phases => {
            // Clear existing options
            phaseSelect.innerHTML = '<option value="">Выберите этап</option>';
            
            // Add new options
            phases.forEach(phase => {
                const option = document.createElement('option');
                option.value = phase.id;
                option.textContent = phase.name;
                phaseSelect.appendChild(option);
            });
        })
        .catch(error => console.error('Error loading growth phases:', error));
    
    eventTypeSelect.addEventListener('change', function() {
        const selectedValue = this.value;
        
        // Hide all conditional fields
        phaseField.style.display = 'none';
        fertilizationFields.style.display = 'none';
        document.getElementById('note_photo_field').style.display = 'none';
        
        // Show appropriate field based on selection
        if (selectedValue === 'growth_phase') {
            phaseField.style.display = 'block';
        } else if (selectedValue === 'fertilization') {
            fertilizationFields.style.display = 'block';
        }
        
        // Show photo field for all event types since photos can be useful for documenting any event
        if (selectedValue !== '') {
            document.getElementById('note_photo_field').style.display = 'block';
        }
    });
    
    // Set today's date as default for event date
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('event_date').value = today;
});

// Function to delete plant (will be called from inline onclick in templates)
function confirmDeletePlant(plantId) {
    if (confirm('Вы уверены, что хотите удалить это растение? Все данные будут потеряны.')) {
        // Create and submit a form for deletion
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = '/delete_plant/' + plantId;
        document.body.appendChild(form);
        form.submit();
    }
}

// Function to delete location (will be called from inline onclick in templates)
function confirmDeleteLocation(locationId) {
    if (confirm('Вы уверены, что хотите удалить эту локацию? Все растения в этой локации будут перемещены в "Без локации".')) {
        // Create and submit a form for deletion
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = '/delete_location/' + locationId;
        document.body.appendChild(form);
        form.submit();
    }
}