<!doctype html>
<html lang="pt-br">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{% block title %}SiGI{% endblock %}</title>

    <!-- Bootstrap e ícones -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css" rel="stylesheet">

    <!-- CSS global -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/base.css') }}">
    {% block extra_css %}{% endblock %}
  </head>
  <body>
    <!-- Navbar -->
    {% if not hide_navbar %}
    <div class="fixed-top">
      <!-- Linha superior: nome -->
      <div class="navbar-top d-flex align-items-center justify-content-between">
        <a class="navbar-brand fw-bold" href="{{ url_for('dashboard.dashboard') }}">
          SiGI
        </a>
      </div>

      <!-- Linha inferior: links -->
      <nav class="navbar navbar-expand-lg navbar-bottom">
        <div class="container-fluid">
          <!-- Botão hamburger -->
          <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarBottomMenu" aria-controls="navbarBottomMenu" aria-expanded="false" aria-label="Toggle navigation">
            <span class="navbar-toggler-icon"></span>
          </button>

          <!-- Links colapsáveis -->
          <div class="collapse navbar-collapse" id="navbarBottomMenu">
            <ul class="navbar-nav me-auto mb-2 mb-lg-0">
              <li class="nav-item">
                <a class="nav-link {% block nav_dashboard_active %}{% endblock %}" href="{{ url_for('dashboard.dashboard') }}">
                  <i class="bi bi-speedometer2 me-1"></i> Dashboard
                </a>
              </li>

              <!-- Secretaria -->
              <li class="nav-item dropdown">
                <a class="nav-link dropdown-toggle" href="#" id="navbarDropdownSecretaria" role="button"
                   data-bs-toggle="dropdown" aria-expanded="false">
                  <i class="bi bi-people-fill me-1"></i> Secretaria
                </a>
                <ul class="dropdown-menu" aria-labelledby="navbarDropdownSecretaria">
                  <li>
                    <a class="dropdown-item" href="{{ url_for('member.listar_membros') }}">
                      <i class="bi bi-person-badge me-1"></i> Membros
                    </a>
                  </li>
                  <li>
                    <a class="dropdown-item" href="{{ url_for('member.relatorio_membros') }}">
                      <i class="bi bi-bar-chart-line me-1"></i> Relatório de Membros
                    </a>
                  </li>
                </ul>
              </li>

              <!-- Eventos -->
              <li class="nav-item dropdown">
                <a class="nav-link dropdown-toggle" href="#" id="navbarDropdownEventos" role="button"
                   data-bs-toggle="dropdown" aria-expanded="false">
                  <i class="bi bi-calendar-event me-1"></i> Eventos
                </a>
                <ul class="dropdown-menu" aria-labelledby="navbarDropdownEventos">
                  <li>
                    <a class="dropdown-item" href="{{ url_for('event.listar_eventos') }}">
                      <i class="bi bi-calendar-event me-1"></i> Todos os Eventos
                    </a>
                  </li>
                  <li>
                    <a class="dropdown-item" href="{{ url_for('member.aniversariantes_mes') }}">
                      <i class="bi bi-gift me-1"></i> Aniversariantes
                    </a>
                  </li>
                </ul>
              </li>

              <!-- Patrimônio -->
              <li class="nav-item dropdown">
                <a class="nav-link dropdown-toggle" href="#" id="navbarDropdownPatrimonio" role="button"
                   data-bs-toggle="dropdown" aria-expanded="false">
                  <i class="bi bi-box-seam me-1"></i> Patrimônio
                </a>
                <ul class="dropdown-menu" aria-labelledby="navbarDropdownPatrimonio">
                  <li>
                    <a class="dropdown-item" href="{{ url_for('patrimonio.listar_patrimonios') }}">
                      <i class="bi bi-box-seam me-1"></i> Todos os Patrimônios
                    </a>
                  </li>
                  <li>
                    <a class="dropdown-item" href="{{ url_for('patrimonio.inventario') }}">
                      <i class="bi bi-clipboard-data me-1"></i> Inventário
                    </a>
                  </li>
                </ul>
              </li>

		<!-- Financeiro -->
		<li class="nav-item">
		  <a class="nav-link {% block nav_financeiro_active %}{% endblock %}" href="{{ url_for('financeiro.financeiro') }}">
		    <i class="bi bi-cash-coin me-1"></i> Financeiro
		  </a>
		</li>

              <!-- Logout -->
              <li class="nav-item">
                <a class="nav-link text-warning" href="{{ url_for('auth.logout') }}">
                  <i class="bi bi-box-arrow-right me-1"></i> Sair
                </a>
              </li>
            </ul>
          </div>
        </div>
      </nav>
    </div>
    {% endif %}

    <!-- Mensagens flash -->
    <div class="position-fixed top-0 start-50 translate-middle-x mt-3" style="z-index: 1080; width: min(600px, 95vw);">
      {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
          {% for category, message in messages %}
            <div class="alert alert-{{ category }} alert-dismissible fade show shadow" role="alert">
              {{ message }}
              <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
          {% endfor %}
        {% endif %}
      {% endwith %}
    </div>

    <!-- Conteúdo -->
    <main class="content-wrap">
      {% block content %}{% endblock %}
    </main>

	{% if not hide_footer %}
	<footer>
	  <div>
	    © 2025 SiGI - Sistema Integrado de Gestão de Igreja<br>
	    Desenvolvido com ❤️ por 
	    <a href="https://github.com/soarespaullo" target="_blank">Paulo Soares</a>
	  </div>
	</footer>
	{% endif %}

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>

    <!-- Auto-dismiss das flash messages em 5s -->
    <script>
      setTimeout(function() {
        document.querySelectorAll('.alert').forEach(function(el) {
          const alert = new bootstrap.Alert(el);
          alert.close();
        });
      }, 5000);
    </script>
  </body>
</html>
