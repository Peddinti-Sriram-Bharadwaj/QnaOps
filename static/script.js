// static/script.js
const form = document.getElementById('question-form');
const questionInput = document.getElementById('question-input');
const answerArea = document.getElementById('answer-area');
const answerText = document.getElementById('answer-text');
const helpfulBtn = document.getElementById('helpful-btn');
const unhelpfulBtn = document.getElementById('unhelpful-btn');
const feedbackMsg = document.getElementById('feedback-msg');
const shareBtn = document.getElementById('share-btn');
const shareLinkInput = document.getElementById('share-link');
const popularList = document.getElementById('popular-questions-list');
const loader = document.getElementById('loader');
const errorMsg = document.getElementById('error-message');

let currentQaId = null; // Store the ID of the current Q&A

// --- API Base URL ---
// Adjust if your FastAPI app is served under a different base path
// This assumes the API is at /api/v1 relative to the domain root
const API_BASE_URL = "/api/v1";

// --- Helper Functions ---
function showLoader() { loader.style.display = 'block'; }
function hideLoader() { loader.style.display = 'none'; }
function showError(message) { errorMsg.textContent = message; errorMsg.style.display = 'block'; }
function hideError() { errorMsg.style.display = 'none'; }
function disableFeedbackButtons() {
    helpfulBtn.disabled = true;
    unhelpfulBtn.disabled = true;
}
 function enableFeedbackButtons() {
    helpfulBtn.disabled = false;
    unhelpfulBtn.disabled = false;
    feedbackMsg.textContent = ''; // Clear previous feedback message
}

// --- Event Listeners ---
form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const question = questionInput.value.trim();
    if (!question) return;

    showLoader();
    hideError();
    answerArea.style.display = 'none'; // Hide previous answer
    currentQaId = null; // Reset current ID
    shareLinkInput.style.display = 'none'; // Hide share link input
    shareLinkInput.value = ''; // Clear previous link
    enableFeedbackButtons(); // Ensure feedback buttons are enabled for new question

    try {
        // Note the path change due to the router prefix
        const response = await fetch(`${API_BASE_URL}/qna/ask`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question: question })
        });

        if (!response.ok) {
            let errorDetail = `HTTP error! status: ${response.status}`;
            try {
                const errorData = await response.json();
                errorDetail = errorData.detail || errorDetail;
            } catch (e) { /* Ignore if response is not JSON */ }
            throw new Error(errorDetail);
        }

        const data = await response.json(); // Expects { qa_id, question, answer }

        answerText.textContent = data.answer;
        currentQaId = data.qa_id; // Store the ID for feedback/sharing
        answerArea.style.display = 'block';
        // Feedback buttons are already enabled here

    } catch (error) {
        console.error('Error asking question:', error);
        showError(`Failed to get answer: ${error.message}`);
    } finally {
        hideLoader();
    }
});

helpfulBtn.addEventListener('click', () => sendFeedback('helpful'));
unhelpfulBtn.addEventListener('click', () => sendFeedback('unhelpful'));

shareBtn.addEventListener('click', () => {
    if (currentQaId) {
        // Construct the shareable link using the backend endpoint directly
        // This assumes your backend serves the shared page or you have another mechanism
        const shareUrl = `${window.location.origin}${API_BASE_URL}/qna/qa/${currentQaId}`;
        // If you have a dedicated frontend page:
        // const shareUrl = `${window.location.origin}/shared.html?qa_id=${currentQaId}`;

        shareLinkInput.value = shareUrl;
        shareLinkInput.style.display = 'inline-block';
        shareLinkInput.select(); // Select text for easy copying
        try {
            // Use Clipboard API for modern browsers
            navigator.clipboard.writeText(shareUrl).then(() => {
                 alert('Share link copied to clipboard!');
            }).catch(err => {
                 console.warn('Could not copy link automatically using Clipboard API.', err);
                 // Fallback for older browsers (less reliable)
                 try {
                    document.execCommand('copy');
                    alert('Share link copied to clipboard! (fallback)');
                 } catch (fallbackErr) {
                    console.warn('Fallback copy command failed.', fallbackErr);
                    alert('Could not copy link. Please copy it manually.');
                 }
            });
        } catch (err) {
             console.warn('Clipboard API not available.', err);
             alert('Could not copy link. Please copy it manually.');
        }
    }
});


// --- Functions ---
async function sendFeedback(rating) {
    if (!currentQaId) return;

    disableFeedbackButtons(); // Prevent multiple clicks
    feedbackMsg.textContent = 'Submitting...';
    feedbackMsg.style.color = 'orange';


    try {
         // Note the path change due to the router prefix
        const response = await fetch(`${API_BASE_URL}/qna/feedback/${currentQaId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ rating: rating })
        });

        if (!response.ok) {
             let errorDetail = `HTTP error! status: ${response.status}`;
             try {
                const errorData = await response.json();
                errorDetail = errorData.detail || errorDetail;
             } catch(e) { /* Ignore if response is not JSON */ }
            throw new Error(errorDetail);
        }

        feedbackMsg.textContent = 'Thanks for your feedback!';
        feedbackMsg.style.color = 'green';
        // Keep buttons disabled after successful feedback for this answer

    } catch (error) {
        console.error('Error submitting feedback:', error);
        feedbackMsg.textContent = `Error: ${error.message}`;
        feedbackMsg.style.color = 'red';
        // Re-enable buttons on error so user can retry
         enableFeedbackButtons();
         feedbackMsg.textContent = `Error submitting. Please try again.`;

    }
}

async function loadPopularQuestions() {
    popularList.innerHTML = 'Loading...'; // Show loading state
    try {
        // Note the path change due to the router prefix
        const response = await fetch(`${API_BASE_URL}/qna/popular-questions?limit=5`);
         if (!response.ok) {
            let errorDetail = `HTTP error! status: ${response.status}`;
             try {
                const errorData = await response.json();
                errorDetail = errorData.detail || errorDetail;
             } catch(e) { /* Ignore if response is not JSON */ }
            throw new Error(errorDetail);
        }
        const questions = await response.json(); // Expects List[PopularQuestion]

        if (!Array.isArray(questions) || questions.length === 0) {
             popularList.innerHTML = '<p>No popular questions yet.</p>';
             return;
        }

        const listHtml = questions.map(q => {
            // Link to the shared view using the direct API endpoint
             const shareUrl = `${window.location.origin}${API_BASE_URL}/qna/qa/${q.id}`;
             // If using a dedicated frontend page:
             // const shareUrl = `${window.location.origin}/shared.html?qa_id=${q.id}`;
             // Escape question text to prevent potential XSS if displayed directly from user input elsewhere
             const escapedQuestion = q.question.replace(/</g, "&lt;").replace(/>/g, "&gt;");
             return `<li><a href="${shareUrl}" target="_blank" title="${escapedQuestion}">${escapedQuestion.substring(0, 30)}${escapedQuestion.length > 30 ? '...' : ''}</a> (${q.view_count} views)</li>`;
            }
        ).join('');
        popularList.innerHTML = `<ul>${listHtml}</ul>`;

    } catch (error) {
         console.error('Error loading popular questions:', error);
         popularList.innerHTML = `<p style="color: red;">Could not load popular questions.</p>`; // Avoid showing raw error message
    }
}

// --- Initial Load ---
loadPopularQuestions();
