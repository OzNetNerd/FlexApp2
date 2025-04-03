# Debug Panel Implementation Guide

## Overview

The debug panel is a reusable component that provides consistent debugging information across your Flask application templates. It's designed to be:

1. Only visible in development mode
2. Easily added to any template
3. Customizable with context-specific information
4. Togglable (expandable/collapsible)
5. Equipped with logging capabilities

## Setup Instructions

### 1. Create the Debug Panel Template

Save the `_debug_panel.html` template to your shared components directory:

```
app/templates/shared/components/_debug_panel.html
```

### 2. Include the Debug Panel in Your Templates

Add the debug panel to any template by including it with the appropriate context:

```jinja2
{% with 
  template_name="my_current_template.html", 
  debug_id="unique_id",
  debug_title="My Component Debug", 
  debug_data={
    "key1": value1,
    "key2": value2
  }
%}
  {% include 'shared/components/_debug_panel.html' %}
{% endwith %}
```

### 3. Using the JavaScript Logger

From your JavaScript code, you can log information to the debug panel:

```javascript
// Check if debug logger is available first
if (window.debugLogger && window.debugLogger.my_panel_id) {
  // Log information
  window.debugLogger.my_panel_id.info("Some information");
  
  // Log warning
  window.debugLogger.my_panel_id.warn("Warning message");
  
  // Log error
  window.debugLogger.my_panel_id.error("Error message");
  
  // Log with data object
  window.debugLogger.my_panel_id.debug("Data objects", {
    key1: "value1",
    key2: "value2"
  });
}
```

## Configuration Options

When including the debug panel, you can provide these context variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `template_name` | Current template name | Based on request.endpoint |
| `debug_id` | Unique ID for this debug panel | "main" |
| `debug_title` | Title displayed in panel header | template_name |
| `debug_data` | Dictionary of debug data to display | None |
| `debug_context` | Additional context information | None |
| `debug_severity` | Panel severity ("info", "warning", "error") | "info" |
| `debug_show_toggle` | Whether to show the toggle button | true |
| `debug_expanded` | Whether panel is expanded by default | false |
| `debug_capture_console` | Capture console.log etc. in panel | false |

## Example: Error Debugging

To display an error debug panel:

```jinja2
{% with 
  template_name="my_template.html", 
  debug_id="error_panel",
  debug_title="Error Information", 
  debug_severity="error",
  debug_expanded=true,
  debug_data={
    "error_code": error_code,
    "error_message": error_message
  }
%}
  {% include 'shared/components/_debug_panel.html' %}
{% endwith %}
```

## Common Use Cases

### 1. Template Context Debugging

Display available template variables:

```jinja2
{% with 
  debug_data={
    "available_vars": {
      "item": item.__class__.__name__ if item else None,
      "user": current_user.username if current_user else None,
      # Add other variables as needed
    }
  }
%}
  {% include 'shared/components/_debug_panel.html' %}
{% endwith %}
```

### 2. Form Validation Debugging

Track form validation issues:

```jinja2
{% with 
  debug_id="form_debug",
  debug_title="Form Validation Debug", 
  debug_data={
    "form_errors": form.errors if form else {},
    "validation_failed": validation_failed
  }
%}
  {% include 'shared/components/_debug_panel.html' %}
{% endwith %}
```

## Security Note

The debug panel only appears when the Flask app is in development mode (`ENV='development'` or `DEBUG=True`). Make sure your production environment has these settings disabled.

## Troubleshooting

If the debug panel doesn't appear:
1. Verify your Flask app is in development mode
2. Check that the template path is correct
3. Ensure all required context variables are provided

If logging doesn't work:
1. Make sure you're using the correct debug_id
2. Check for JavaScript errors in the console
3. Verify the debug panel is properly initialized