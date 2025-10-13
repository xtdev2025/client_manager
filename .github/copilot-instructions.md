# Copilot Instructions for xPages/client_manager

This document provides guidelines for GitHub Copilot to ensure all contributions align with our project's goals, particularly focusing on Design, Usability, User Experience (UX), and Lead Conversion.

## Core Principles

When generating or modifying code, especially on the frontend, prioritize the following principles:

1.  **User-Centric Design:** The user is at the center of all decisions. Interfaces should be intuitive, easy to navigate, and solve user problems efficiently.
2.  **Conversion-Oriented:** Every page, component, and interaction should, where appropriate, guide the user towards a conversion goal (e.g., signing up, contacting sales, starting a trial).
3.  **Seamless Usability:** Remove friction. Workflows should be logical, require minimal effort, and prevent errors.
4.  **Consistent & Modern Aesthetics:** Maintain a consistent visual identity that is clean, modern, and professional.

## Design & UX Guidelines

*   **Visual Hierarchy:** Ensure a clear visual hierarchy. The most important elements (like CTAs) should be prominent. Use size, color, and placement to guide the user's attention.
*   **Whitespace:** Use whitespace effectively to reduce cognitive load and improve readability. Avoid cluttered interfaces.
*   **Color Palette:** Adhere to the project's established color palette. Use colors purposefully (e.g., primary color for main actions, accent colors for secondary actions, and reds/oranges for warnings).
*   **Typography:** Use a limited set of clean, legible fonts. Ensure font sizes and line heights are optimized for readability across all devices.
*   **Responsiveness:** All UI components and pages MUST be fully responsive and provide an excellent experience on desktop, tablet, and mobile devices. Mobile-first design is preferred.
*   **Accessibility (a11y):** Design for everyone. Use semantic HTML, provide alt text for images, ensure sufficient color contrast, and make sure the application is navigable via keyboard.

## Usability & Interaction

*   **Clarity & Simplicity:** "Don't make me think." Labels, instructions, and navigation should be clear and unambiguous.
*   **Feedback:** Provide immediate and clear feedback for user actions (e.g., loading states, success messages, validation errors).
*   **Error Handling:** Design helpful, non-intrusive error messages that explain what went wrong and how to fix it.
*   **Performance:** Optimize for speed. Lazy-load images and non-critical resources. Minimize asset sizes. A slow page is a high-friction page.

## Lead Conversion Focus

*   **Clear Calls-to-Action (CTAs):** CTAs should be visually distinct, use action-oriented language (e.g., "Start Your Free Trial," "Get a Demo"), and be strategically placed.
*   **Value Proposition:** Clearly communicate the benefits of the product/service on landing pages. Answer the user's question: "What's in it for me?"
*   **Trust Signals:** Incorporate elements that build trust, such as testimonials, customer logos, security badges, and clear privacy policies.
*   **Forms:** Keep forms as short as possible. Only ask for essential information. Use multi-step forms for longer processes if necessary. Clearly label fields and provide inline validation.
*   **A/B Testing Mindset:** When implementing UI changes, consider how they could be tested. For example, creating components that can easily have their text or color changed for A/B testing purposes.

## When Generating Code

*   **Frameworks & Libraries:** Use the existing frontend frameworks and libraries (e.g., Flask for templating, any specific CSS framework if present).
*   **Component-Based:** Think in terms of reusable components. If a UI element is used in multiple places, it should be a candidate for a reusable template or macro.
*   **Semantic HTML:** Write clean, semantic HTML5. Use tags like `<header>`, `<footer>`, `<nav>`, `<main>`, `<section>`, and `<article>` appropriately.
*   **Clean CSS:** Follow a consistent naming convention (like BEM) if one is in place. Keep CSS modular and easy to maintain.
