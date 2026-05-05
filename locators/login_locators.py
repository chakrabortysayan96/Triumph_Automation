class LoginLocators:

    # --- App Login Page ---
    # The Azure SSO button shown on the application's own login screen.
    # Clicking this redirects to the Microsoft sign-in flow.
    AZURE_SSO_TEXT = "Azure"

    # --- Microsoft Sign-In: Email Step ---
    # Placeholder text of the email/username input on the Microsoft login page.
    EMAIL_PLACEHOLDER = "Email, phone, or Skype"
    # "Next" button that advances from the email step to the password step.
    NEXT_BUTTON_NAME = "Next"

    # --- Microsoft Sign-In: Password Step ---
    # Placeholder text of the password input field.
    PASSWORD_PLACEHOLDER = "Password"
    # "Sign in" button that submits credentials and triggers authentication.
    SIGN_IN_BUTTON_NAME = "Sign in"

    # --- Post-Login: Stay Signed In Prompt ---
    # Optional dialog Microsoft shows after a successful sign-in.
    # Clicking "Yes" keeps the session alive; the prompt may not always appear.
    STAY_SIGNED_IN_BUTTON_NAME = "Yes"

    # --- Post-Login Navigation ---
    # URL glob pattern used to confirm the browser has landed inside the app
    # after a successful login.
    POST_LOGIN_URL_PATTERN = "**/ap-invoice-management/**"
