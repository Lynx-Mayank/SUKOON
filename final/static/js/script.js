// Simple state management
let threadsData = [];
let isAnonymous = false;
let bookings = [];

// Initialize the app
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    loadSampleData();
    updateStats();
});

function initializeApp() {
    // Toggle anonymous posting
    document.getElementById('toggle-anon').addEventListener('click', function() {
        isAnonymous = !isAnonymous;
        this.textContent = isAnonymous ? 'Post as Yourself' : 'Post Anonymously';
        this.style.background = isAnonymous ? '#5f9ea0' : '#f9a6a3';
        this.style.color = isAnonymous ? 'white' : '#1a1a2e';
    });

    // Post new thread
    document.getElementById('post-thread').addEventListener('click', function() {
        postNewThread();
    });

    // Appointment booking
    document.getElementById('save-appt').addEventListener('click', function() {
        saveAppointment();
    });

    // Enter key to post
    document.getElementById('new-thread-title').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            document.getElementById('new-thread-body').focus();
        }
    });
}

function loadSampleData() {
    // Sample threads with proper structure (oldest to newest in data)
    threadsData = [
        {
            id: 3,
            title: "Managing work-study balance",
            description: "Working 20 hours/week while taking full course load. Struggling to keep up with assignments and feel constantly tired.",
            author: "WorkingStudent",
            timestamp: "1d ago",
            replies: [
                {
                    author: "Senior2025",
                    content: "Been there! Time blocking saved my life. Schedule everything including sleep and meals. Also talk to your professors about your situation."
                },
                {
                    author: "Anonymous",
                    content: "Check if your school has resources for working students. Mine had priority registration and special study spaces."
                }
            ]
        },
        {
            id: 2,
            title: "Feeling isolated in dorms",
            description: "I'm a first-year student and having trouble connecting with people in my dorm. Everyone seems to have their friend groups already. Feeling pretty lonely.",
            author: "FirstYear2024",
            timestamp: "5h ago",
            replies: [
                {
                    author: "RA_Helper",
                    content: "Join some clubs or study groups! It's a great way to meet people with similar interests. The semester is still young."
                }
            ]
        },
        {
            id: 1,
            title: "Exam stress — need tips",
            description: "I have three exams next week and I'm feeling overwhelmed. My anxiety is making it hard to focus on studying. Anyone have strategies that helped them?",
            author: "Anonymous",
            timestamp: "2h ago",
            replies: [
                {
                    author: "StudyBuddy",
                    content: "Try the Pomodoro technique! 25 min study, 5 min break. It really helped me manage my anxiety during finals."
                },
                {
                    author: "Anonymous",
                    content: "Deep breathing exercises before each study session work wonders. Also, break your syllabus into smaller chunks."
                }
            ]
        }
    ];

    renderThreads();
}

function renderThreads() {
    const threadsList = document.getElementById('threads-list');
    threadsList.innerHTML = '';

    threadsData.forEach(thread => {
        const threadElement = createThreadElement(thread);
        threadsList.appendChild(threadElement);
    });
}

function createThreadElement(thread) {
    const threadDiv = document.createElement('div');
    threadDiv.className = 'thread';
    
    // Create replies HTML
    let repliesHTML = '';
    if (thread.replies && thread.replies.length > 0) {
        repliesHTML = `
            <div class="thread-replies">
                ${thread.replies.map(reply => `
                    <div class="reply">
                        <div class="reply-author">${reply.author}</div>
                        ${reply.content}
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    threadDiv.innerHTML = `
        <div class="thread-content">
            <div class="thread-header">
                <h4 class="thread-title">${thread.title}</h4>
                <div class="thread-meta">by ${thread.author} • ${thread.timestamp}</div>
            </div>
            <p class="thread-description">${thread.description}</p>
            ${repliesHTML}
            <div class="reply-form" id="reply-form-${thread.id}" style="display:none;">
                <textarea id="reply-text-${thread.id}" placeholder="Write your reply..." rows="2" style="width:100%;padding:0.5rem;border-radius:6px;border:1px solid rgba(0,0,0,0.1);margin-bottom:0.5rem;"></textarea>
                <div style="display:flex;gap:0.5rem;justify-content:flex-end;">
                    <button class="btn secondary" onclick="cancelReply(${thread.id})">Cancel</button>
                    <button class="btn" onclick="submitReply(${thread.id})">Reply</button>
                </div>
            </div>
            <div class="thread-actions" style="margin-top:0.5rem;padding-top:0.5rem;border-top:1px solid rgba(0,0,0,0.05);">
                <button class="btn secondary" onclick="showReplyForm(${thread.id})" style="font-size:0.85rem;padding:0.4rem 0.6rem;">Reply</button>
            </div>
        </div>
    `;
    
    return threadDiv;
}

function postNewThread() {
    const title = document.getElementById('new-thread-title').value.trim();
    const body = document.getElementById('new-thread-body').value.trim();
    
    if (!title || !body) {
        alert('Please fill in both title and description');
        return;
    }

    const newThread = {
        id: threadsData.length + 1,
        title: title,
        description: body,
        author: isAnonymous ? 'Anonymous' : 'You',
        timestamp: 'just now',
        replies: []
    };

    threadsData.unshift(newThread); // Add to beginning
    renderThreads();
    
    // Clear form
    document.getElementById('new-thread-title').value = '';
    document.getElementById('new-thread-body').value = '';
    
    updateStats();
}

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.classList.add('show');
    
    // Set default date to today
    if (modalId === 'apptModal') {
        const today = new Date().toISOString().split('T')[0];
        document.getElementById('date').value = today;
    }
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('show');
}

function saveAppointment() {
    const name = document.getElementById('stu-name').value;
    const contact = document.getElementById('stu-contact').value;
    const counselor = document.getElementById('counselor').value;
    const date = document.getElementById('date').value;
    const time = document.getElementById('time').value;

    if (!date || !time) {
        alert('Please select both date and time');
        return;
    }

    const booking = {
        id: bookings.length + 1,
        name: name || 'Anonymous',
        contact: contact || 'Not provided',
        counselor: counselor,
        date: date,
        time: time,
        timestamp: new Date().toISOString()
    };

    bookings.push(booking);
    
    // Clear form
    document.getElementById('stu-name').value = '';
    document.getElementById('stu-contact').value = '';
    document.getElementById('date').value = '';
    document.getElementById('time').value = '';
    
    closeModal('apptModal');
    alert('Appointment booked successfully! (Demo mode - no real booking made)');
    
    updateStats();
}

function updateStats() {
    const threadCount = document.getElementById('stat-threads');
    const bookingCount = document.getElementById('stat-bookings');
    
    if (threadCount) threadCount.textContent = threadsData.length;
    if (bookingCount) bookingCount.textContent = bookings.length;
}

// Close modal when clicking outside
window.addEventListener('click', function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.classList.remove('show');
    }
});

// ESC key to close modal
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        document.querySelectorAll('.modal.show').forEach(modal => {
            modal.classList.remove('show');
        });
    }
});

// Reply functionality
function showReplyForm(threadId) {
    const replyForm = document.getElementById(`reply-form-${threadId}`);
    const replyButton = document.querySelector(`button[onclick="showReplyForm(${threadId})"]`);
    
    replyForm.style.display = 'block';
    replyButton.style.display = 'none';
    
    // Focus on the textarea
    document.getElementById(`reply-text-${threadId}`).focus();
}

function cancelReply(threadId) {
    const replyForm = document.getElementById(`reply-form-${threadId}`);
    const replyButton = document.querySelector(`button[onclick="showReplyForm(${threadId})"]`);
    const replyText = document.getElementById(`reply-text-${threadId}`);
    
    replyForm.style.display = 'none';
    replyButton.style.display = 'inline-block';
    replyText.value = '';
}

function submitReply(threadId) {
    const replyText = document.getElementById(`reply-text-${threadId}`);
    const text = replyText.value.trim();
    
    if (!text) {
        alert('Please write a reply');
        return;
    }
    
    // Find the thread and add the reply
    const thread = threadsData.find(t => t.id === threadId);
    if (thread) {
        if (!thread.replies) {
            thread.replies = [];
        }
        
        thread.replies.push({
            author: isAnonymous ? 'Anonymous' : 'You',
            content: text
        });
        
        // Re-render threads to show the new reply
        renderThreads();
    }
}