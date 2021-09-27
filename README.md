<p>
    <img alt="Rolls-Royce Logo" width="100" src="https://raw.githubusercontent.com/rropen/.github/main/img/logo.png">
    <br>
    Dashboard for Rolls-Royce Software Factory Metrics
</p>

<!-- Place any useful shield.io shields here.  Use the style=flat styling option. -->
<p>
    <a href="https://github.com/rropen/SFM"><img src="https://img.shields.io/badge/Rolls--Royce-Software%20Factory-10069f"></a>
    <a href="https://github.com/rropen/SFM/actions/workflows/frontend_unit_tests.yml"><img src="https://github.com/rropen/SFM/actions/workflows/frontend_unit_tests.yml/badge.svg"></a>
    <a href="https://github.com/rropen/SFM/actions/workflows/backend_unit_tests.yml"><img src="https://github.com/rropen/SFM/actions/workflows/backend_unit_tests.yml/badge.svg"></a>
    <a href="https://github.com/rropen/SFM/actions/workflows/integration_tests.yml"><img src="https://github.com/rropen/SFM/actions/workflows/integration_tests.yml/badge.svg"></a>
</p>

---
    
<p>
    <a href="http://commitizen.github.io/cz-cli/"><img src="https://img.shields.io/badge/commitizen-friendly-brightgreen?style=flat"></a>
    <a href="https://www.cypress.io/"><img src="https://img.shields.io/badge/tested%20with-Cypress-04C38E?style=flat">
    <a href="https://v3.vuejs.org/"><img src="https://img.shields.io/badge/vuejs-%2335495e.svg?style=flat&logo=vuedotjs&logoColor=%234FC08D"></a>
    <a href="https://tailwindcss.com/"><img src="https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=flat&logo=tailwind-css&logoColor=white"></a>
    <a href="https://www.typescriptlang.org/"><img src="https://img.shields.io/badge/typescript-%23007ACC.svg?style=flat&logo=typescript&logoColor=white"></a>
</p>

## Overview

This project is intended to provide a way for the Rolls-Royce Software Factory to track and display it's [DORA](https://www.devops-research.com/research.html) metrics in accordance with modern DevSecOps [best practices](https://itrevolution.com/measure-software-delivery-performance-four-key-metrics/). As we continue in our Digital Transformation and align ourselves with the DoD's [efforts](https://software.af.mil/wp-content/uploads/2021/05/Digital-Building-Code-and-Scorecard-Memo-v15.pdf) around DevSecOps we need to track these metrics. Initially we'll start with the [four key](https://cloud.google.com/blog/products/devops-sre/using-the-four-keys-to-measure-your-devops-performance) metrics and likely scale out from there as appropriate.

We're also investigating the use of the [Flow Framework](https://projecttoproduct.org/) and how we might use it to better align our value stream to usable metrics.

Initial plans for this project are to use our standard "Modern" architecture:

Frontend:

- [Vue.js](https://vuejs.org/) (V3, composition API)
- TypeScript & [TailwindCSS](https://tailwindcss.com/)

Backend:

- [FastAPI](https://fastapi.tiangolo.com/) (Python, Rest Endpoints)
- [SqlModel](https://sqlmodel.tiangolo.com/) as ORM/SQL Helper Layer

## Usage

TBD

## Visibility

This project is meant to be in the open source - public facing region of the Rolls-Royce GitHub Enterprise instance. Any secrets or secure configuration information will be handled through the use of secure secrets and other cloud native ways. If any features or updates need to be added to this project that would push it out of the public facing organization, then it will be moved. Contact [Josh Haines](mailto:Josh.Haines@Rolls-Royce.com) if you have any questions.
