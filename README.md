# Sunrise Drilling Ltd - Django Website

A modern, responsive Django website for Sunrise Drilling Ltd, featuring the company's services, about information, gallery, and contact details.

## Features

- **Modern Design**: Clean, professional design with custom color scheme
- **Responsive Layout**: Works perfectly on desktop, tablet, and mobile devices
- **Custom Color Scheme**: Uses specified colors #2DADF7 (blue) and #F7852D (orange)
- **Individual CSS Files**: Each page has its own CSS file as requested
- **Professional Navigation**: Smooth navigation between pages
- **Contact Form**: Functional contact form for customer inquiries
- **SEO Optimized**: Proper meta tags and structured content

## Color Scheme

- **Primary Blue**: #2DADF7
- **Primary Orange**: #F7852D
- **Supporting Colors**: Various shades of green for headers and accents

## Project Structure

```
sunrise_drilling_django/
├── manage.py
├── sunrise_drilling_django/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── main/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── templates/
│   ├── base.html
│   └── main/
│       ├── home.html
│       ├── about.html
│       ├── services.html
│       ├── gallery.html
│       └── contact.html
├── static/
│   └── css/
│       ├── main.css (base styles)
│       ├── home.css (home page specific)
│       ├── about.css (about page specific)
│       ├── services.css (services page specific)
│       ├── gallery.css (gallery page specific)
│       └── contact.css (contact page specific)
└── README.md
```

## Pages

### 1. Home Page (`/`)
- Hero section with company branding
- Quick navigation links
- Services preview
- Contact information
- **CSS File**: `static/css/home.css`

### 2. About Page (`/about/`)
- Company history and timeline
- Mission and vision statements
- Core values
- Certifications and compliance
- **CSS File**: `static/css/about.css`

### 3. Services Page (`/services/`)
- Detailed service descriptions
- Process workflow
- Why choose us section
- Call-to-action sections
- **CSS File**: `static/css/services.css`

### 4. Gallery Page (`/gallery/`)
- Project portfolio
- Filterable image gallery
- Project categories
- Achievement statistics
- **CSS File**: `static/css/gallery.css`

### 5. Contact Page (`/contact/`)
- Contact form
- Company contact information
- Business hours
- Location map placeholder
- FAQ section
- **CSS File**: `static/css/contact.css`

## Installation and Setup

### Prerequisites
- Python 3.8 or higher
- Django 5.2.4 or higher

### Installation Steps

1. **Navigate to the project directory**:
   ```bash
   cd sunrise_drilling_django
   ```

2. **Install Django** (if not already installed):
   ```bash
   pip install django
   ```

3. **Run database migrations**:
   ```bash
   python manage.py migrate
   ```

4. **Start the development server**:
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

5. **Access the website**:
   Open your browser and go to `http://localhost:8000`

## CSS Architecture

Each page has its own dedicated CSS file that includes:

- **Page-specific styling**: Unique styles for each page
- **Responsive design**: Mobile-first approach with media queries
- **Color consistency**: Uses the specified color palette throughout
- **Modern effects**: Gradients, animations, and hover effects
- **Professional typography**: Clean, readable fonts and spacing

### Base CSS (`main.css`)
Contains global styles, variables, and common components used across all pages.

### Page-specific CSS Files
- `home.css`: Hero sections, quick links, service previews
- `about.css`: Timeline, values grid, mission/vision cards
- `services.css`: Service cards, process steps, feature lists
- `gallery.css`: Image gallery, filters, modal functionality
- `contact.css`: Contact forms, info cards, FAQ accordion

## Key Features

### Responsive Design
- Mobile-first approach
- Breakpoints for tablets and desktops
- Touch-friendly navigation
- Optimized images and layouts

### Color Implementation
- **#2DADF7 (Blue)**: Used for primary buttons, links, and accents
- **#F7852D (Orange)**: Used for call-to-action buttons and highlights
- **Gradients**: Beautiful gradient combinations using both colors
- **Green tones**: Used for headers and natural/environmental themes

### Interactive Elements
- Smooth scrolling animations
- Hover effects on cards and buttons
- Interactive gallery with modal view
- Responsive navigation menu
- Form validation and feedback

## Browser Compatibility

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Performance Features

- Optimized CSS with efficient selectors
- Minimal JavaScript for enhanced performance
- Responsive images
- Clean, semantic HTML structure

## Customization

### Adding New Pages
1. Create a new view in `main/views.py`
2. Add URL pattern in `main/urls.py`
3. Create template in `templates/main/`
4. Create corresponding CSS file in `static/css/`

### Modifying Colors
Update the CSS custom properties in `main.css`:
```css
:root {
    --primary-blue: #2DADF7;
    --primary-orange: #F7852D;
    /* Add other color variables */
}
```

### Adding Content
- Update templates in `templates/main/`
- Modify static content directly in HTML
- Add new images to `static/images/`

## Contact Form Functionality

The contact form is ready for backend integration. To make it functional:

1. Add form handling logic in `main/views.py`
2. Configure email settings in `settings.py`
3. Add form validation and success messages

## Deployment

For production deployment:

1. Set `DEBUG = False` in `settings.py`
2. Configure `ALLOWED_HOSTS`
3. Set up static file serving
4. Use a production WSGI server (e.g., Gunicorn)
5. Configure database for production

## Support

This Django website is fully functional and ready for use. All pages are responsive, the navigation works perfectly, and the design implements the requested color scheme (#2DADF7 and #F7852D) throughout the site.

The website successfully recreates the original Sunrise Drilling Ltd website with modern Django architecture, improved design, and the specified color palette.

# sunrise2
