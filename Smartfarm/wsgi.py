"""
WSGI config for Smartfarm project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os
import sys
import traceback

from django.core.wsgi import get_wsgi_application

# Add the project directory to the Python path
path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if path not in sys.path:
    sys.path.append(path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Smartfarm.settings')

try:
    application = get_wsgi_application()
    
    # Test if the application is working correctly
    print("WSGI application initialized successfully")
    
except Exception as e:
    # Log the error for debugging
    print("Error loading application:", file=sys.stderr)
    traceback.print_exc()
    
    # Create a simple error application to show what went wrong
    def simple_error_application(environ, start_response):
        status = '500 Internal Server Error'
        headers = [('Content-type', 'text/html')]
        start_response(status, headers)
        error_message = traceback.format_exc()
        response = f"""
        <html>
            <head>
                <title>Server Error</title>
                <style>
                    body {{ font-family: Arial, sans-serif; padding: 20px; }}
                    .error {{ background: #f8d7da; padding: 20px; border-radius: 5px; }}
                    pre {{ background: #f8f9fa; padding: 15px; overflow: auto; }}
                </style>
            </head>
            <body>
                <h1>Server Error</h1>
                <div class="error">
                    <p><strong>There was an error initializing the application.</strong></p>
                    <p>Please check your server logs for more information.</p>
                </div>
                <h3>Technical Details:</h3>
                <pre>{error_message}</pre>
            </body>
        </html>
        """
        return [response.encode('utf-8')]
    
    application = simple_error_application
