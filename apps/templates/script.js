// cookies
const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

// loading line
document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("article-form");
    const loaderLine = document.querySelector(".loader-line");

    form.addEventListener("submit", function (event) {
            event.preventDefault(); // Prevent default form submission behavior

            const articleUrl = document.getElementById("article-url").value; // Get the value from the input field

            const jsonData = {
                "url": articleUrl
            };

            if (articleUrl !== '') {
                // show the loader element
                loaderLine.style.visibility = "visible";

                const xhr = new XMLHttpRequest();
                xhr.open("POST", "{% url 'articles' %}", true);
                xhr.setRequestHeader("Content-Type", "application/json");
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
                xhr.onreadystatechange = function () {
                    if (xhr.readyState === XMLHttpRequest.DONE) {
                        if (xhr.status === 200) {
                            console.log("Article URL sent successfully!");
                            setTimeout(function () {
                                document.getElementById("article-url").value = '';
                                loaderLine.style.visibility = "hidden";
                                location.reload();
                            }, 3000);

                        } else if (xhr.status === 201) {
                            console.log("Existing Article is successfully added!");
                            setTimeout(function () {
                                document.getElementById("article-url").value = '';
                                loaderLine.style.visibility = "hidden";
                                location.reload();
                            }, 1000);

                        } else {
                            console.error("Error sending article URL:", xhr.statusText);
                            document.getElementById("article-url").value = '';
                        }
                    }
                }
                ;
                xhr.send(JSON.stringify(jsonData));
            }
        }
    )
    ;
});


document.addEventListener("DOMContentLoaded", function () {
    const iframe = document.getElementById("article-iframe");
    const articleButtons = document.querySelectorAll(".article-button");

    // Add click event listener to each article button
    articleButtons.forEach(button => {
        button.addEventListener("click", function () {
            const articleId = button.getAttribute("data-article-id");

            // Fetch the article content using AJAX
            fetch(`/api/v1/articles/${articleId}/`, {
                method: "GET",
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken,
                },
                mode: 'same-origin',
            })
                .then(response => response.json())
                .then(content => {
                    // Set the iframe's srcdoc attribute to the fetched content
                    iframe.srcdoc = content.data;
                })
                .catch(error => {
                    console.error("Error fetching article content:", error);
                });
        });
    });

    iframe.addEventListener("load", function () {
        const iframeContent = iframe.contentDocument || iframe.contentWindow.document;
        const translationPopover = document.getElementById("translationPopover");
        const originalTextElement = document.getElementById("originalText");
        const translatedTextElement = document.getElementById("translatedText");
        const addToDictionaryButton = document.getElementById("addToDictionary");

        // Variables to store the position of the selected text
        let selectedTextRect = null;

        iframeContent.addEventListener("mouseup", function () {
            const selectedText = iframeContent.getSelection().toString().trim();

            if (selectedText !== "") {
                // Store the position of the selected text
                const selection = iframeContent.getSelection();
                const range = selection.getRangeAt(0);
                selectedTextRect = range.getBoundingClientRect();

                // Send the selected text to the translation endpoint
                translateSelectedText(selectedText);
            } else {
                // Hide the popover if no text is selected
                translationPopover.style.display = "none";
                selectedTextRect = null;
            }
        });

        addToDictionaryButton.addEventListener("click", function () {
            const originalText = originalTextElement.textContent.replace("English: ", "");
            const translationText = translatedTextElement.textContent.replace("Ukrainian: ", "");

            // Send the original word and translation to the dictionary endpoint
            addToDictionary(originalText, translationText);
        });


        function translateSelectedText(text) {
            const translationData = {
                word: text
            };

            fetch('/api/v1/dictionary/translate/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken,
                },
                mode: 'same-origin',
                body: JSON.stringify(translationData)
            })
                .then(response => response.json())
                .then(data => {
                    // Update the popover content with original and translated text
                    originalTextElement.textContent = "English: " + text;
                    translatedTextElement.textContent = "Ukrainian: " + data.translation;

                    // Show the popover and set its position
                    translationPopover.style.display = "block";

                    // Calculate the initial top position of the popover
                    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
                    const top = selectedTextRect.top + scrollTop - translationPopover.clientHeight - 10;
                    translationPopover.style.top = top + "px";

                    // Calculate the initial left position of the popover (centered horizontally)
                    const left = selectedTextRect.left + selectedTextRect.width / 2 - translationPopover.clientWidth / 2;
                    translationPopover.style.left = left + "px";
                })
                .catch(error => {
                    console.error('Error during translation:', error);
                });
        }

        // Function to add a word to the dictionary
        function addToDictionary(originalText, translationText) {
            const dictionaryData = {
                word: originalText,
                translation: translationText
            };

            fetch('/api/v1/dictionary/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken,
                },
                mode: 'same-origin',
                body: JSON.stringify(dictionaryData)
            })
                .then(response => {
                    if (response.ok) {
                        console.log('Word added to dictionary:', originalText, translationText);
                        // After successfully adding the word, update the vocabulary list
                        updateVocabularyList();
                    } else {
                        console.error('Error adding word to dictionary:', response.statusText);
                    }
                })
                .catch(error => {
                    console.error('Error adding word to dictionary:', error);
                });
        }

// Function to update the vocabulary list
        function updateVocabularyList() {
            fetch('/api/v1/dictionary/', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                mode: 'same-origin',
            })
                .then(response => response.json())
                .then(data => {
                    const wordUl = document.getElementById('word-ul');
                    wordUl.innerHTML = '';

                    data.forEach(word => {
                        const listItem = document.createElement('li');
                        listItem.className = 'nav-item pb-3 li-word-button';
                        listItem.innerHTML = `
                <div style="display: flex; margin: 0; padding: 0" class="btn btn-outline-secondary text-truncate overflow-hidden col-sm-4">
                    <button class="word-button btn" style="width: 25em" tabindex="0" type="button"
                        data-bs-toggle="popover" data-bs-trigger="focus" data-bs-title="${word.word}" data-bs-content="${word.translation}"
                        data-word-id="${word.id}">${word.word}</button>
                    <button class="btn fa-solid fa-xmark word-rm" data-word-id="${word.id}" style="width: 50px;"></button>
                </div>
            `;
                        wordUl.appendChild(listItem);

                        const rmButton = listItem.querySelector(".word-rm");
                        rmButton.addEventListener("click", function () {
                            const wordId = rmButton.getAttribute("data-word-id");
                            const li = rmButton.closest(".li-word-button");

                            fetch(`/api/v1/dictionary/${wordId}/`, {
                                method: "DELETE",
                                headers: {
                                    'Content-Type': 'application/json',
                                    'X-CSRFToken': csrftoken,
                                },
                                mode: 'same-origin',
                            })
                                .then(response => {
                                    if (response.status === 200) {
                                        console.log('Word removed successfully');
                                        $(li).fadeOut(300, function () {
                                            li.remove();
                                        });
                                    } else {
                                        console.error('Word removal failed');
                                    }
                                })
                                .catch(error => {
                                    console.error('Error during word removal:', error);
                                });
                        });
                    });

                    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
                    const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));
                })
                .catch(error => {
                    console.error('Error updating vocabulary list:', error);
                });
        }

// Call updateVocabularyList() to initially populate the list
        updateVocabularyList();

    });


});

// Function to handle the logout process
function logout() {
    fetch('/api/v1/logout/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        mode: 'same-origin',
    })
        .then(response => {
            if (response.status === 200) {
                // Successful logout
                console.log('User logged out successfully');
                // Redirect or update UI as needed
                window.location.href = '/'; // Redirect to the home page, for example
            } else {
                // Handle logout failure, e.g., display an error message
                console.error('Logout failed');
            }
        })
        .catch(error => {
            // Handle network errors or other issues
            console.error('Error during logout:', error);
        });
}

// Attach an event listener to the "Log out" link
document.addEventListener('DOMContentLoaded', function () {
    const logoutLink = document.querySelector('#logout-link');

    if (logoutLink) {
        logoutLink.addEventListener('click', function (event) {
            event.preventDefault(); // Prevent the link from navigating
            logout(); // Call the logout function when the link is clicked
        });
    }
});

// Function to handle the login process
function login() {
    const usernameOrEmail = document.querySelector('#login-form input[type="text"]').value;
    const password = document.querySelector('#login-form input[type="password"]').value;

    // Prepare the login data
    const loginData = {
        username_or_email: usernameOrEmail,
        password: password
    };

    // Send an AJAX request to log in
    fetch('/api/v1/login/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        mode: 'same-origin',
        body: JSON.stringify(loginData)
    })
        .then(response => {
            if (response.status === 200) {
                // Successful login
                console.log('User logged in successfully');
                location.reload();
                // Redirect or update UI as needed
            } else {
                // Handle login failure, e.g., display an error message
                console.error('Login failed');
            }
        })
        .catch(error => {
            // Handle network errors or other issues
            console.error('Error during login:', error);
        });
}

// Function to handle the sign-up process
function signup() {
    const username = document.querySelector('#signup-form input[type="text"]').value;
    const email = document.querySelector('#signup-form input[type="email"]').value;
    const password = document.querySelector('#signup-form input[type="password"]').value;

    // Prepare the registration data
    const registrationData = {
        username: username,
        email: email,
        password: password
    };

    // Send an AJAX request to register
    fetch('/api/v1/signup/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        mode: 'same-origin',
        body: JSON.stringify(registrationData)
    })
        .then(response => {
            if (response.status === 201) {
                // Successful registration
                console.log('User registered successfully');
                // Redirect or update UI as needed
                location.reload();
            } else {
                // Handle registration failure, e.g., display an error message
                console.error('Registration failed');
            }
        })
        .catch(error => {
            // Handle network errors or other issues
            console.error('Error during registration:', error);
        });
}

// Attach event listeners to the "Login" and "Register" buttons
document.addEventListener('DOMContentLoaded', function () {
    const loginButton = document.querySelector('#login-form .btn-outline-primary');
    const signupButton = document.querySelector('#signup-form .btn-outline-primary');
    const loginInput = document.querySelector('#login-form');
    const signupInput = document.querySelector('#signup-form');

    // Listen for Enter key press on the password input fields for both forms
    loginInput.addEventListener('keyup', function (event) {
        if (event.key === 'Enter') {
            login();
        }
    });

    signupInput.addEventListener('keyup', function (event) {
        if (event.key === 'Enter') {
            signup();
        }
    });

    if (loginButton) {
        loginButton.addEventListener('click', function (event) {
            event.preventDefault();
            login();
        });
    }

    if (signupButton) {
        signupButton.addEventListener('click', function (event) {
            event.preventDefault();
            signup();
        });
    }
});

// word search
document.addEventListener("DOMContentLoaded", function () {
    const searchInput = document.getElementById("search-input");
    const wordList = document.getElementById("word-list");

    searchInput.addEventListener("input", function () {
        const searchTerm = searchInput.value.trim().toLowerCase();

        // Get all li elements with the class "li-word-button"
        const wordLiElements = wordList.querySelectorAll(".li-word-button");

        // Loop through the li elements and hide/show based on the search term
        wordLiElements.forEach(function (li) {
            const button = li.querySelector(".word-button");
            const word = button.textContent.toLowerCase();
            if (word.includes(searchTerm)) {
                $(li).fadeIn(300);// Show matching words
            } else {
                $(li).fadeOut(300); // Hide non-matching words
            }
        });
    });
});

// remove buttons
document.addEventListener("DOMContentLoaded", function () {
    const articleButtons = document.querySelectorAll(".article-rm");
    articleButtons.forEach(button => {
        button.addEventListener("click", function () {
            const articleId = button.getAttribute("data-article-id");
            const li = button.closest(`.li-article-button`)

            // Fetch the article content using AJAX
            fetch(`/api/v1/articles/${articleId}/`, {
                method: "DELETE",
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken,
                },
                mode: 'same-origin',
            })
                .then(response => {
                    if (response.status === 200) {
                        // Successful logout
                        console.log('Article removed successfully');
                        $(li).fadeOut(300, function () {
                            li.remove();
                        });
                    } else {
                        // Handle logout failure, e.g., display an error message
                        console.error('Article removal failed');
                    }
                })
                .catch(error => {
                    // Handle network errors or other issues
                    console.error('Error during article removal:', error);
                });
        });
    });
});


// jQuery animation for nav
$(function () {
    // Calling Login Form
    $("#vocabulary-btn").click(function () {
        $(".saved-articles").fadeOut(300, function () {
            $(".saved-vocabulary").fadeIn(300);
        });
        return false;
    });

    // Calling Register Form
    $("#articles-btn").click(function () {
        $(".saved-vocabulary").fadeOut(300, function () {
            $(".saved-articles").fadeIn(300);
        });
        return false;
    });
});

// jQuery animation for auth
$(function () {
    // Calling Login Form
    $("#login_form").click(function () {
        $(".social_login").fadeOut(300, function () {
            $(".user_login").fadeIn(300);
        });
        return false;
    });

    // Calling Register Form
    $("#register_form").click(function () {
        $(".social_login").fadeOut(300, function () {
            $(".user_register").fadeIn(300);
            $(".header_title").text('Register');
        });
        return false;
    });

    // Going back to Social Forms
    $(".login-back").click(function () {
        $(".user_login").fadeOut(300, function () {
            $(".social_login").fadeIn(300);
            $(".header_title").text('Login');
        });
        return false;
    });

    $(".register-back").click(function () {
        $(".user_register").fadeOut(300, function () {
            $(".social_login").fadeIn(300);
            $(".header_title").text('Login');
        });
        return false;
    });
});
