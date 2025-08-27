# AgriConnect

AgriConnect is a Django web application that connects farmers, experts, and customers in the agricultural sector.

## Local Development

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Create a `.env` file with the following variables:
   ```
   DEBUG=True
   SECRET_KEY=your_secret_key
   EMAIL_HOST_USER=your_email@example.com
   EMAIL_HOST_PASSWORD=your_app_password
   DEFAULT_FROM_EMAIL=AgriConnect <your_email@example.com>
   RAZOR_KEY_ID=your_razorpay_key_id
   RAZOR_KEY_SECRET=your_razorpay_key_secret
   ```
5. Run migrations:
   ```
   python manage.py migrate
   ```
6. Start the development server:
   ```
   python manage.py runserver
   ```

## Deployment on Render

### Automatic Deployment

1. Fork this repository
2. Create a new Web Service on Render, connected to your GitHub repository
3. Select "Python" as the environment
4. Set the build command to `./build.sh`
5. Set the start command to `gunicorn Smartfarm.wsgi:application`
6. Add the following environment variables:
   - `SECRET_KEY`: Generate a secure secret key
   - `DEBUG`: Set to "False"
   - `EMAIL_HOST_USER`: Your email address
   - `EMAIL_HOST_PASSWORD`: Your email app password
   - `DEFAULT_FROM_EMAIL`: Your default sender email
   - `RAZOR_KEY_ID`: Your Razorpay Key ID
   - `RAZOR_KEY_SECRET`: Your Razorpay Key Secret
7. Set up a PostgreSQL database on Render
8. Link the database to your web service by adding the `DATABASE_URL` environment variable

### Manual Deployment

You can also deploy manually using the `render.yaml` configuration file in this repository:

1. Create a new PostgreSQL database on Render
2. Copy its External URL
3. Use the Render Dashboard Blueprint feature with this repository URL
4. Follow the prompts, adding the external database URL when asked

## Features

- Multiple user roles: farmers, experts, and customers
- Product management and listings
- Expert advice platform
- Administrative dashboard
- User management
- Payment integration with Razorpay.
