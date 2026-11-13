/* ============================================================
   Lost & Found Portal — Police Station Edition
   Vanilla JS • No frameworks • No jQuery
   ============================================================ */

(function () {
  'use strict';

  /* --- state: who's logged in, kept around for the whole session --- */
  let currentUser = null;

  /* ==========================================================
     Core Utilities
     ========================================================== */

  /* --- api: single gateway for every server call --- */
  async function api(url, options = {}) {
    const defaults = {
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
    };
    if (options.body && typeof options.body === 'object') {
      options.body = JSON.stringify(options.body);
    }
    const res = await fetch(url, { ...defaults, ...options });
    if (!res.ok) {
      let msg = 'Something went wrong';
      try {
        const data = await res.json();
        msg = data.error || data.message || msg;
      } catch (_) { /* non-JSON error body */ }
      throw new Error(msg);
    }
    /* some endpoints (204) return no body */
    const text = await res.text();
    return text ? JSON.parse(text) : null;
  }

  /* --- toast: nothing fancy, just a heads-up that fades away --- */
  function showToast(message, type = 'info') {
    let container = document.querySelector('.toast-container');
    if (!container) {
      container = document.createElement('div');
      container.className = 'toast-container';
      document.body.appendChild(container);
    }
    const toast = document.createElement('div');
    toast.className = 'toast toast-' + type;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(function () {
      if (toast.parentNode) toast.parentNode.removeChild(toast);
    }, 4000);
  }

  /* --- dates: dd/mm/yyyy the way India writes them --- */
  function formatDate(dateStr) {
    if (!dateStr) return '—';
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return dateStr;
    var dd = String(d.getDate()).padStart(2, '0');
    var mm = String(d.getMonth() + 1).padStart(2, '0');
    var yyyy = d.getFullYear();
    return dd + '/' + mm + '/' + yyyy;
  }

  /* --- url: read query params without fuss --- */
  function getUrlParam(name) {
    return new URLSearchParams(window.location.search).get(name);
  }

  /* --- debounce: wait for the typist to pause --- */
  function debounce(fn, ms) {
    let timer;
    return function () {
      var ctx = this, args = arguments;
      clearTimeout(timer);
      timer = setTimeout(function () { fn.apply(ctx, args); }, ms);
    };
  }

  /* --- placeholder SVG for cards with no image --- */
  var noImageSVG =
    '<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" ' +
    'fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" ' +
    'stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/>' +
    '<circle cx="8.5" cy="8.5" r="1.5"/><path d="m21 15-5-5L5 21"/></svg>';


  /* ==========================================================
     Auth State
     ========================================================== */

  /* --- auth: figure out who we are before anything else runs --- */
  async function checkAuth() {
    try {
      currentUser = await api('/api/auth/me');
    } catch (_) {
      currentUser = null;
    }
    updateNav();
  }

  function updateNav() {
    /* show / hide nav links based on role */
    var navLinks = document.querySelectorAll('[data-auth]');
    navLinks.forEach(function (el) {
      var rule = el.getAttribute('data-auth');
      if (rule === 'guest') {
        el.style.display = currentUser ? 'none' : '';
      } else if (rule === 'user') {
        el.style.display = currentUser ? '' : 'none';
      } else if (rule === 'citizen') {
        el.style.display = (currentUser && currentUser.role === 'citizen') ? '' : 'none';
      } else if (rule === 'police') {
        el.style.display = (currentUser && currentUser.role === 'police') ? '' : 'none';
      }
    });

    var navDashboard = document.getElementById('nav-dashboard');
    var navPolice = document.getElementById('nav-police-dashboard');
    var navLogin = document.getElementById('nav-login');
    var navLogout = document.getElementById('nav-logout');

    if (currentUser) {
      if (navLogin) navLogin.style.display = 'none';
      if (navLogout) navLogout.style.display = '';
      if (navDashboard) navDashboard.style.display = currentUser.role === 'citizen' ? '' : 'none';
      if (navPolice) navPolice.style.display = currentUser.role === 'police' ? '' : 'none';
    } else {
      if (navLogin) navLogin.style.display = '';
      if (navLogout) navLogout.style.display = 'none';
      if (navDashboard) navDashboard.style.display = 'none';
      if (navPolice) navPolice.style.display = 'none';
    }

    var stationSpan = document.getElementById('station-name');
    if (stationSpan) {
      if (currentUser && currentUser.police_station) {
        stationSpan.textContent = currentUser.police_station;
      } else {
        stationSpan.textContent = 'Kotwali Police Station, Lucknow';
      }
    }
  }

  function requireAuth() {
    if (!currentUser) {
      window.location.href = '/login.html';
      return false;
    }
    return true;
  }


  /* ==========================================================
     Nav Hamburger
     ========================================================== */

  /* --- hamburger: tap and the links drop down --- */
  function initHamburger() {
    var btns = document.querySelectorAll('.hamburger, .nav-toggle');
    var header = document.querySelector('.site-header');
    if (header) {
      btns.forEach(function (btn) {
        btn.addEventListener('click', function () {
          header.classList.toggle('nav-open');
        });
      });
    }
  }


  /* ==========================================================
     Page: Home (index.html)
     ========================================================== */

  /* --- home: load the board of property notices --- */
  function initHomePage() {
    var grid = document.getElementById('properties-grid');
    if (!grid) return;

    var currentPage = 1;
    var totalPages = 1;

    function buildQuery() {
      var params = new URLSearchParams();
      var q = document.getElementById('filter-search') || document.getElementById('search-input');
      var typeChecked = document.querySelector('input[name="type"]:checked');
      var type = typeChecked ? typeChecked.value : (document.getElementById('filter-type') ? document.getElementById('filter-type').value : '');
      var category = document.getElementById('filter-category');
      var status = document.getElementById('filter-status');
      var station = document.getElementById('filter-station');
      var dateFrom = document.getElementById('filter-date-from');
      var dateTo = document.getElementById('filter-date-to');

      if (q && q.value.trim()) params.set('q', q.value.trim());
      if (type) params.set('type', type);
      if (category && category.value) params.set('category', category.value);
      if (status && status.value) params.set('status', status.value);
      if (station && station.value) params.set('station', station.value);
      if (dateFrom && dateFrom.value) params.set('date_from', dateFrom.value);
      if (dateTo && dateTo.value) params.set('date_to', dateTo.value);
      params.set('page', currentPage);
      return params.toString();
    }

    /* --- filters: rebuild the grid every time a filter changes --- */
    async function loadProperties() {
      try {
        var data = await api('/api/properties?' + buildQuery());
        renderGrid(data.properties || data.items || []);
        totalPages = data.pages || data.total_pages || 1;
        currentPage = data.page || data.current_page || 1;
        renderPagination();
      } catch (err) {
        showToast(err.message, 'error');
      }
    }

    function renderGrid(items) {
      if (!items.length) {
        grid.innerHTML =
          '<p class="text-center mt-4" style="color:var(--text-secondary);grid-column:1/-1">' +
          'No properties found. Try adjusting your filters.</p>';
        return;
      }
      grid.innerHTML = items.map(function (p) {
        var imgHtml = p.image_url
          ? '<div class="card-image"><img src="' + p.image_url + '" alt="' + (p.title || 'Property') + '"></div>'
          : '<div class="card-image"><span class="no-image">' + noImageSVG + '</span></div>';

        var typeBadge = p.type === 'lost'
          ? '<span class="badge badge-lost">Lost</span>'
          : '<span class="badge badge-unclaimed">Unclaimed</span>';

        var statusBadge = '<span class="badge badge-' + (p.status || 'pending') + '">' + (p.status || 'pending') + '</span>';
        var catBadge = p.category ? '<span class="badge badge-category">' + p.category + '</span>' : '';

        return (
          '<div class="property-card">' +
            imgHtml +
            '<div class="card-meta">' + typeBadge + statusBadge + catBadge + '</div>' +
            '<div class="card-title"><a href="/property.html?id=' + p.id + '">' + (p.title || 'Untitled') + '</a></div>' +
            '<div class="card-desc">' + (p.description || '').substring(0, 120) + '</div>' +
            '<div class="card-footer">' +
              '<span>' + formatDate(p.date_lost || p.created_at) + '</span>' +
              '<span>' + (p.police_station || '') + '</span>' +
            '</div>' +
          '</div>'
        );
      }).join('');
    }

    function renderPagination() {
      var pag = document.getElementById('pagination');
      if (!pag) return;
      pag.innerHTML =
        '<button class="btn btn-secondary btn-small" id="prev-page" ' + (currentPage <= 1 ? 'disabled' : '') + '>&larr; Previous</button>' +
        '<span class="page-info">Page ' + currentPage + ' of ' + totalPages + '</span>' +
        '<button class="btn btn-secondary btn-small" id="next-page" ' + (currentPage >= totalPages ? 'disabled' : '') + '>Next &rarr;</button>';

      document.getElementById('prev-page').addEventListener('click', function () {
        if (currentPage > 1) { currentPage--; loadProperties(); }
      });
      document.getElementById('next-page').addEventListener('click', function () {
        if (currentPage < totalPages) { currentPage++; loadProperties(); }
      });
    }

    /* attach filter listeners */
    ['filter-type', 'filter-category', 'filter-status', 'filter-station',
     'filter-date-from', 'filter-date-to'].forEach(function (id) {
      var el = document.getElementById(id);
      if (el) el.addEventListener('change', function () { currentPage = 1; loadProperties(); });
    });

    document.querySelectorAll('input[name="type"]').forEach(function (radio) {
      radio.addEventListener('change', function () { currentPage = 1; loadProperties(); });
    });

    var filterForm = document.getElementById('filter-form');
    if (filterForm) {
      filterForm.addEventListener('submit', function (e) {
        e.preventDefault();
        currentPage = 1;
        loadProperties();
      });
      filterForm.addEventListener('reset', function () {
        setTimeout(function () { currentPage = 1; loadProperties(); }, 50);
      });
    }

    var searchInputs = [document.getElementById('filter-search'), document.getElementById('search-input')];
    searchInputs.forEach(function (si) {
      if (si) {
        si.addEventListener('input', debounce(function () { currentPage = 1; loadProperties(); }, 300));
        si.addEventListener('keypress', function (e) {
          if (e.key === 'Enter') {
            e.preventDefault();
            currentPage = 1;
            loadProperties();
          }
        });
      }
    });

    var searchBtn = document.getElementById('search-btn');
    if (searchBtn) {
      searchBtn.addEventListener('click', function () { currentPage = 1; loadProperties(); });
    }

    /* filter sidebar toggle on mobile */
    var toggleBtn = document.querySelector('.filter-toggle-btn');
    var sidebar = document.querySelector('.filter-sidebar');
    if (toggleBtn && sidebar) {
      toggleBtn.addEventListener('click', function () {
        sidebar.classList.toggle('open');
        toggleBtn.textContent = sidebar.classList.contains('open') ? 'Hide Filters' : 'Show Filters';
      });
    }

    loadProperties();
  }


  /* ==========================================================
     Page: Report Lost Property
     ========================================================== */

  /* --- report-lost: citizen fills in the notice --- */
  function initReportLostPage() {
    var form = document.getElementById('report-lost-form');
    if (!form) return;
    if (!requireAuth()) return;

    initImagePreview(form);

    form.addEventListener('submit', async function (e) {
      e.preventDefault();

      /* client-side required field check */
      if (!form.checkValidity()) {
        form.reportValidity();
        return;
      }

      /* --- masking: we never want the full ID number leaving the browser --- */
      var idNumber = form.querySelector('[name="id_proof_number"]');
      var maskedId = '';
      if (idNumber && idNumber.value) {
        maskedId = idNumber.value.slice(-4);
      }

      var body = {
        type: 'lost',
        applicant_name: val(form, 'applicant_name'),
        address: val(form, 'address'),
        phone: val(form, 'phone'),
        id_proof_type: val(form, 'id_proof_type'),
        id_proof_masked: maskedId,
        category: val(form, 'category'),
        title: val(form, 'title'),
        description: val(form, 'description'),
        how_lost: val(form, 'how_lost'),
        date_lost: val(form, 'date_lost'),
        time_lost: val(form, 'time_lost'),
        location_lost: val(form, 'location_lost'),
        police_station: val(form, 'police_station'),
        declaration_accepted: (form.querySelector('[name="declaration_accepted"]') && form.querySelector('[name="declaration_accepted"]').checked) ||
                              (form.querySelector('[name="declaration"]') && form.querySelector('[name="declaration"]').checked) ||
                              (form.querySelector('#declaration') && form.querySelector('#declaration').checked),
        consent_accepted: (form.querySelector('[name="consent_accepted"]') && form.querySelector('[name="consent_accepted"]').checked) ||
                          (form.querySelector('[name="consent"]') && form.querySelector('[name="consent"]').checked) ||
                          (form.querySelector('#consent') && form.querySelector('#consent').checked),
      };

      /* image (base64) */
      var fileInput = form.querySelector('[name="image"]');
      if (fileInput && fileInput.files && fileInput.files[0]) {
        var file = fileInput.files[0];
        if (file.size > 2 * 1024 * 1024) {
          showToast('Image must be under 2 MB', 'error');
          return;
        }
        body.image = await readFileAsBase64(file);
      }

      try {
        var result = await api('/api/properties', { method: 'POST', body: body });
        form.style.display = 'none';
        showAcknowledgement(result);
        showToast('Report submitted successfully', 'success');
      } catch (err) {
        showToast(err.message, 'error');
      }
    });
  }


  /* ==========================================================
     Page: Report Unclaimed Property
     ========================================================== */

  /* --- report-unclaimed: police officer logs a found item --- */
  function initReportUnclaimedPage() {
    var form = document.getElementById('report-unclaimed-form');
    if (!form) return;
    if (!requireAuth()) return;

    initImagePreview(form);

    form.addEventListener('submit', async function (e) {
      e.preventDefault();
      if (!form.checkValidity()) { form.reportValidity(); return; }

      var body = {
        type: 'unclaimed',
        applicant_name: val(form, 'applicant_name'),
        address: val(form, 'address'),
        phone: val(form, 'phone'),
        category: val(form, 'category'),
        title: val(form, 'title'),
        description: val(form, 'description'),
        date_lost: val(form, 'date_found'),
        location_lost: val(form, 'location_found'),
        police_station: val(form, 'police_station'),
        officer_name: val(form, 'officer_name'),
        officer_badge_id: val(form, 'officer_badge_id'),
        current_location: val(form, 'current_location'),
        declaration_accepted: (form.querySelector('[name="declaration_accepted"]') && form.querySelector('[name="declaration_accepted"]').checked) ||
                              (form.querySelector('[name="declaration"]') && form.querySelector('[name="declaration"]').checked) ||
                              (form.querySelector('#declaration') && form.querySelector('#declaration').checked),
        consent_accepted: (form.querySelector('[name="consent_accepted"]') && form.querySelector('[name="consent_accepted"]').checked) ||
                          (form.querySelector('[name="consent"]') && form.querySelector('[name="consent"]').checked) ||
                          (form.querySelector('#consent') && form.querySelector('#consent').checked),
      };

      var fileInput = form.querySelector('[name="image"]');
      if (fileInput && fileInput.files && fileInput.files[0]) {
        var file = fileInput.files[0];
        if (file.size > 2 * 1024 * 1024) { showToast('Image must be under 2 MB', 'error'); return; }
        body.image = await readFileAsBase64(file);
      }

      try {
        var result = await api('/api/properties', { method: 'POST', body: body });
        form.style.display = 'none';
        showAcknowledgement(result);
        showToast('Unclaimed property registered', 'success');
      } catch (err) {
        showToast(err.message, 'error');
      }
    });
  }


  /* ==========================================================
     Page: Property Detail
     ========================================================== */

  /* --- detail: everything about one notice --- */
  function initPropertyDetailPage() {
    var detailEl = document.getElementById('property-detail');
    if (!detailEl) return;

    var id = getUrlParam('id');
    if (!id) { detailEl.innerHTML = '<p>No property ID specified.</p>'; return; }

    (async function () {
      try {
        var p = await api('/api/properties/' + id);
        renderDetail(detailEl, p);
      } catch (err) {
        detailEl.innerHTML = '<p>Could not load property: ' + err.message + '</p>';
      }
    })();

    function renderDetail(el, p) {
      var imgHtml = p.image_url
        ? '<img class="detail-image" src="' + p.image_url + '" alt="' + (p.title || '') + '">'
        : '';

      var typeBadge = p.type === 'lost'
        ? '<span class="badge badge-lost">Lost</span>'
        : '<span class="badge badge-unclaimed">Unclaimed</span>';
      var statusBadge = '<span class="badge badge-' + (p.status || 'pending') + '">' + (p.status || 'pending') + '</span>';

      el.innerHTML =
        '<div class="detail-header">' +
          '<h1>' + (p.title || 'Untitled') + '</h1>' +
          '<div class="flex" style="gap:0.5rem;margin-top:0.5rem">' + typeBadge + statusBadge + '</div>' +
        '</div>' +
        imgHtml +
        '<div class="detail-grid">' +
          detailField('Registration #', p.registration_number) +
          detailField('Category', p.category) +
          detailField('Date', formatDate(p.date_lost)) +
          detailField('Time', p.time_lost || '—') +
          detailField('Location', p.location_lost) +
          detailField('Police Station', p.police_station) +
          detailField('Reported By', p.applicant_name) +
          detailField('Contact', p.phone) +
          (p.officer_name ? detailField('Officer', p.officer_name) : '') +
          (p.current_location ? detailField('Kept At', p.current_location) : '') +
        '</div>' +
        '<div class="detail-narrative">' +
          '<h3>Description</h3>' +
          '<p>' + (p.description || '—') + '</p>' +
          (p.how_lost ? '<h3>How It Was Lost</h3><p>' + p.how_lost + '</p>' : '') +
        '</div>' +
        '<div id="claim-section"></div>';

      /* claim button — only if logged in, not the reporter, and not already returned */
      if (currentUser && p.reporter_id !== currentUser.id && p.status !== 'returned') {
        var claimEl = document.getElementById('claim-section');
        claimEl.innerHTML =
          '<div class="claim-section">' +
            '<h3>Claim This Property</h3>' +
            '<form id="claim-form">' +
              '<div class="form-group">' +
                '<label for="claim-message">Why do you believe this is yours?</label>' +
                '<textarea id="claim-message" name="message" required placeholder="Describe identifying features…"></textarea>' +
              '</div>' +
              '<button type="submit" class="btn btn-primary">Submit Claim</button>' +
            '</form>' +
          '</div>';

        document.getElementById('claim-form').addEventListener('submit', async function (ev) {
          ev.preventDefault();
          try {
            await api('/api/properties/' + id + '/claim', {
              method: 'POST',
              body: { message: document.getElementById('claim-message').value },
            });
            showToast('Claim submitted', 'success');
            claimEl.innerHTML = '<p class="mt-2" style="color:var(--accent)">Your claim has been submitted and is awaiting review.</p>';
          } catch (err) {
            showToast(err.message, 'error');
          }
        });
      } else if (!currentUser && p.status !== 'returned') {
        var claimEl = document.getElementById('claim-section');
        if (claimEl) {
          claimEl.innerHTML =
            '<div class="claim-section text-center">' +
              '<h3>Think this property belongs to you?</h3>' +
              '<p class="text-secondary mb-2">You must be logged in as a citizen to submit a legal ownership claim to the police station.</p>' +
              '<a href="/login.html" class="btn btn-primary">Login to Submit Claim</a>' +
            '</div>';
        }
      }
    }

    function detailField(label, value) {
      return (
        '<div class="detail-field">' +
          '<div class="field-label">' + label + '</div>' +
          '<div class="field-value">' + (value || '—') + '</div>' +
        '</div>'
      );
    }
  }


  /* ==========================================================
     Page: Login
     ========================================================== */

  /* --- login: credential check, then redirect --- */
  function initLoginPage() {
    var form = document.getElementById('login-form');
    if (!form) return;

    form.addEventListener('submit', async function (e) {
      e.preventDefault();
      try {
        var user = await api('/api/auth/login', {
          method: 'POST',
          body: {
            email: val(form, 'email'),
            password: val(form, 'password'),
          },
        });
        currentUser = user;
        showToast('Welcome back, ' + user.full_name, 'success');
        setTimeout(function () {
          window.location.href = user.role === 'police' ? '/police-dashboard.html' : '/';
        }, 600);
      } catch (err) {
        showToast(err.message, 'error');
      }
    });
  }


  /* ==========================================================
     Page: Register
     ========================================================== */

  /* --- register: new account, citizen or police --- */
  function initRegisterPage() {
    var form = document.getElementById('register-form');
    if (!form) return;

    /* toggle police-specific fields */
    var roleRadios = form.querySelectorAll('[name="role"]');
    var policeFields = form.querySelector('.police-fields, #police-fields, .conditional-fields');

    roleRadios.forEach(function (r) {
      r.addEventListener('change', function () {
        if (policeFields) {
          var isPolice = r.value === 'police' && r.checked;
          policeFields.classList.toggle('visible', isPolice);
          if (isPolice) {
            policeFields.removeAttribute('hidden');
            policeFields.style.display = 'block';
          } else {
            policeFields.setAttribute('hidden', '');
            policeFields.style.display = 'none';
          }
        }
      });
    });

    form.addEventListener('submit', async function (e) {
      e.preventDefault();
      if (!form.checkValidity()) { form.reportValidity(); return; }

      var body = {
        full_name: val(form, 'full_name'),
        email: val(form, 'email'),
        password: val(form, 'password'),
        phone: val(form, 'phone'),
        role: val(form, 'role') || 'citizen',
      };

      if (body.role === 'police') {
        body.police_station = val(form, 'police_station');
      }

      try {
        await api('/api/auth/register', { method: 'POST', body: body });
        showToast('Account created! Please log in.', 'success');
        setTimeout(function () {
          window.location.href = '/login.html';
        }, 800);
      } catch (err) {
        showToast(err.message, 'error');
      }
    });
  }


  /* ==========================================================
     Page: Citizen Dashboard
     ========================================================== */

  /* --- citizen dashboard: your reports at a glance --- */
  function initDashboardPage() {
    var container = document.getElementById('citizen-dashboard');
    if (!container) return;
    if (!requireAuth()) return;

    var tableBody = document.getElementById('my-reports-body');

    async function load() {
      try {
        var data = await api('/api/properties?reporter=me');
        var items = data.properties || data.items || [];
        if (!tableBody) return;
        if (!items.length) {
          tableBody.innerHTML = '<tr><td colspan="6" class="text-center">No reports yet.</td></tr>';
          return;
        }
        tableBody.innerHTML = items.map(function (p) {
          return (
            '<tr>' +
              '<td>' + (p.registration_number || '—') + '</td>' +
              '<td>' + (p.title || '—') + '</td>' +
              '<td><span class="badge badge-' + p.type + '">' + p.type + '</span></td>' +
              '<td><span class="badge badge-' + p.status + '">' + p.status + '</span></td>' +
              '<td>' + formatDate(p.created_at) + '</td>' +
              '<td class="actions">' +
                '<a href="/property.html?id=' + p.id + '" class="btn btn-secondary btn-small">View</a>' +
                (p.status !== 'returned' ? '<button class="btn btn-danger btn-small" data-delete="' + p.id + '">Delete</button>' : '') +
              '</td>' +
            '</tr>'
          );
        }).join('');

        /* delete handlers */
        tableBody.querySelectorAll('[data-delete]').forEach(function (btn) {
          btn.addEventListener('click', async function () {
            if (!confirm('Are you sure you want to delete this report?')) return;
            try {
              await api('/api/properties/' + btn.getAttribute('data-delete'), { method: 'DELETE' });
              showToast('Report deleted', 'success');
              load();
            } catch (err) {
              showToast(err.message, 'error');
            }
          });
        });
      } catch (err) {
        showToast(err.message, 'error');
      }
    }

    /* DPDP data deletion request */
    var deleteAccountBtn = document.getElementById('request-deletion');
    if (deleteAccountBtn) {
      deleteAccountBtn.addEventListener('click', async function () {
        if (!confirm('This will request deletion of all your data. This action cannot be easily undone. Continue?')) return;
        try {
          await api('/api/users/request-deletion', { method: 'POST' });
          showToast('Deletion request submitted. Your data will be removed within 30 days.', 'info');
        } catch (err) {
          showToast(err.message, 'error');
        }
      });
    }

    load();
  }


  /* ==========================================================
     Page: Police Dashboard
     ========================================================== */

  /* --- police dashboard: the duty desk --- */
  function initPoliceDashboardPage() {
    var container = document.getElementById('police-dashboard');
    if (!container) return;
    if (!requireAuth()) return;

    /* --- tabs: switch between register sections --- */
    initTabs();

    var stationSelect = document.getElementById('station-filter');

    function getStation() {
      return stationSelect ? stationSelect.value : '';
    }

    /* load everything */
    async function loadAll() {
      await Promise.all([
        loadStats(),
        loadProperties(),
        loadClaims(),
        loadAuditLog(),
      ]);
    }

    /* --- stats: quick-glance numbers --- */
    async function loadStats() {
      try {
        var stats = await api('/api/dashboard/stats');
        setText('stat-lost', stats.total_lost);
        setText('stat-unclaimed', stats.total_unclaimed);
        setText('stat-returned', stats.total_returned);
        setText('stat-pending-claims', stats.pending_claims);
      } catch (_) { /* silently fail stats */ }
    }

    /* --- properties tab --- */
    async function loadProperties() {
      try {
        var params = new URLSearchParams();
        var station = getStation();
        if (station) params.set('station', station);
        var data = await api('/api/properties?' + params.toString());
        var items = data.properties || data.items || [];
        var tbody = document.getElementById('properties-body');
        if (!tbody) return;
        if (!items.length) {
          tbody.innerHTML = '<tr><td colspan="7" class="text-center">No properties found.</td></tr>';
          return;
        }
        tbody.innerHTML = items.map(function (p) {
          var actions = '';
          if (p.status === 'pending') {
            actions += '<button class="btn btn-primary btn-small" data-approve="' + p.id + '">Approve</button> ';
          }
          if (p.status !== 'returned') {
            actions += '<button class="btn btn-secondary btn-small" data-return="' + p.id + '">Mark Returned</button> ';
          }
          actions += '<button class="btn btn-secondary btn-small" data-matches="' + p.id + '">Matches</button>';
          return (
            '<tr>' +
              '<td>' + (p.registration_number || '—') + '</td>' +
              '<td>' + (p.title || '—') + '</td>' +
              '<td><span class="badge badge-' + p.type + '">' + p.type + '</span></td>' +
              '<td><span class="badge badge-' + p.status + '">' + p.status + '</span></td>' +
              '<td>' + (p.police_station || '—') + '</td>' +
              '<td>' + formatDate(p.created_at) + '</td>' +
              '<td class="actions">' + actions + '</td>' +
            '</tr>'
          );
        }).join('');

        /* approve handlers */
        tbody.querySelectorAll('[data-approve]').forEach(function (btn) {
          btn.addEventListener('click', async function () {
            try {
              await api('/api/properties/' + btn.getAttribute('data-approve') + '/status', {
                method: 'PATCH', body: { status: 'approved' },
              });
              showToast('Property approved', 'success');
              loadAll();
            } catch (err) { showToast(err.message, 'error'); }
          });
        });

        /* mark returned handlers */
        tbody.querySelectorAll('[data-return]').forEach(function (btn) {
          btn.addEventListener('click', async function () {
            try {
              await api('/api/properties/' + btn.getAttribute('data-return') + '/status', {
                method: 'PATCH', body: { status: 'returned' },
              });
              showToast('Marked as returned', 'success');
              loadAll();
            } catch (err) { showToast(err.message, 'error'); }
          });
        });

        /* matches handlers */
        tbody.querySelectorAll('[data-matches]').forEach(function (btn) {
          btn.addEventListener('click', async function () {
            await showMatches(btn.getAttribute('data-matches'));
          });
        });
      } catch (err) {
        showToast(err.message, 'error');
      }
    }

    /* --- matches panel: show potential matches for a property --- */
    async function showMatches(propertyId) {
      var matchesTab = document.getElementById('tab-matches');
      /* activate matches tab */
      activateTab('tab-matches');
      var matchesList = document.getElementById('matches-list');
      if (!matchesList) return;
      matchesList.innerHTML = '<p>Loading matches…</p>';
      try {
        var data = await api('/api/properties/' + propertyId + '/matches');
        var matches = data.matches || data || [];
        if (!matches.length) {
          matchesList.innerHTML = '<p>No matches found for this property.</p>';
          return;
        }
        matchesList.innerHTML =
          '<h4 class="mb-2">Potential matches for Property #' + propertyId + '</h4>' +
          matches.map(function (m) {
            return (
              '<div class="property-card" style="transform:none;margin-bottom:1rem">' +
                '<div class="card-meta">' +
                  '<span class="badge badge-' + m.type + '">' + m.type + '</span>' +
                  '<span class="badge badge-category">' + (m.category || '') + '</span>' +
                  '<span style="margin-left:auto;font-size:0.85rem;color:var(--text-secondary)">Score: ' + (m.match_score ? m.match_score.toFixed(2) : '—') + '</span>' +
                '</div>' +
                '<div class="card-title"><a href="/property.html?id=' + m.id + '">' + (m.title || 'Untitled') + '</a></div>' +
                '<div class="card-desc">' + (m.description || '').substring(0, 150) + '</div>' +
                '<div class="card-footer"><span>' + formatDate(m.date_lost || m.created_at) + '</span><span>' + (m.police_station || '') + '</span></div>' +
              '</div>'
            );
          }).join('');
      } catch (err) {
        matchesList.innerHTML = '<p>Error loading matches: ' + err.message + '</p>';
      }
    }

    /* --- claims tab --- */
    async function loadClaims() {
      try {
        var data = await api('/api/claims');
        var claims = data.claims || data || [];
        var tbody = document.getElementById('claims-body');
        if (!tbody) return;
        if (!claims.length) {
          tbody.innerHTML = '<tr><td colspan="6" class="text-center">No claims.</td></tr>';
          return;
        }
        tbody.innerHTML = claims.map(function (c) {
          var actions = '';
          if (c.status === 'pending') {
            actions =
              '<button class="btn btn-primary btn-small" data-claim-approve="' + c.id + '">Approve</button> ' +
              '<button class="btn btn-danger btn-small" data-claim-reject="' + c.id + '">Reject</button>';
          } else {
            actions = '<span class="badge badge-' + c.status + '">' + c.status + '</span>';
          }
          return (
            '<tr>' +
              '<td>' + (c.id) + '</td>' +
              '<td>' + (c.property_registration || c.property_id || '—') + '</td>' +
              '<td>' + (c.claimant_name || '—') + '</td>' +
              '<td>' + (c.message || '—').substring(0, 80) + '</td>' +
              '<td>' + formatDate(c.created_at) + '</td>' +
              '<td class="actions">' + actions + '</td>' +
            '</tr>'
          );
        }).join('');

        tbody.querySelectorAll('[data-claim-approve]').forEach(function (btn) {
          btn.addEventListener('click', async function () {
            try {
              await api('/api/claims/' + btn.getAttribute('data-claim-approve'), {
                method: 'PATCH', body: { status: 'approved' },
              });
              showToast('Claim approved', 'success');
              loadAll();
            } catch (err) { showToast(err.message, 'error'); }
          });
        });

        tbody.querySelectorAll('[data-claim-reject]').forEach(function (btn) {
          btn.addEventListener('click', async function () {
            try {
              await api('/api/claims/' + btn.getAttribute('data-claim-reject'), {
                method: 'PATCH', body: { status: 'rejected' },
              });
              showToast('Claim rejected', 'info');
              loadAll();
            } catch (err) { showToast(err.message, 'error'); }
          });
        });
      } catch (err) { showToast(err.message, 'error'); }
    }

    /* --- audit log tab --- */
    async function loadAuditLog() {
      try {
        var data = await api('/api/dashboard/audit-log');
        var entries = data.entries || data.logs || data || [];
        var tbody = document.getElementById('audit-body');
        if (!tbody) return;
        if (!entries.length) {
          tbody.innerHTML = '<tr><td colspan="5" class="text-center">No audit entries.</td></tr>';
          return;
        }
        tbody.innerHTML = entries.map(function (e) {
          return (
            '<tr>' +
              '<td>' + formatDate(e.timestamp || e.created_at) + '</td>' +
              '<td>' + (e.officer_name || e.officer_id || '—') + '</td>' +
              '<td>' + (e.action || '—') + '</td>' +
              '<td>' + (e.property_id || '—') + '</td>' +
              '<td>' + (e.old_value || '—') + ' → ' + (e.new_value || '—') + '</td>' +
            '</tr>'
          );
        }).join('');
      } catch (err) { showToast(err.message, 'error'); }
    }

    /* certificate tab */
    var certForm = document.getElementById('certificate-form');
    if (certForm) {
      certForm.addEventListener('submit', async function (e) {
        e.preventDefault();
        var propId = val(certForm, 'certificate_property_id');
        if (!propId) { showToast('Enter a property ID', 'error'); return; }
        try {
          var data = await api('/api/properties/' + propId + '/certificate', { method: 'POST' });
          var area = document.getElementById('certificate-output');
          if (area) {
            area.innerHTML = data.html || data.certificate || '<p>Certificate generated.</p>';
          }
          showToast('Certificate ready', 'success');
        } catch (err) { showToast(err.message, 'error'); }
      });
    }

    /* station filter reload */
    if (stationSelect) {
      stationSelect.addEventListener('change', function () { loadAll(); });
    }

    loadAll();
  }


  /* ==========================================================
     Tabs helper
     ========================================================== */

  function initTabs() {
    var tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(function (btn) {
      btn.addEventListener('click', function () {
        activateTab(btn.getAttribute('data-tab'));
      });
    });
  }

  function activateTab(tabId) {
    document.querySelectorAll('.tab-btn').forEach(function (b) {
      b.classList.toggle('active', b.getAttribute('data-tab') === tabId);
    });
    document.querySelectorAll('.tab-content').forEach(function (c) {
      c.classList.toggle('active', c.id === tabId);
    });
  }


  /* ==========================================================
     Shared Helpers
     ========================================================== */

  /* quick form value getter */
  function val(form, name) {
    var el = form.querySelector('[name="' + name + '"]');
    if (!el) return '';
    if (el.type === 'radio') {
      var checked = form.querySelector('[name="' + name + '"]:checked');
      return checked ? checked.value : '';
    }
    return el.value.trim();
  }

  /* --- image preview: show a thumbnail when a file is chosen --- */
  function initImagePreview(form) {
    var fileInput = form.querySelector('[name="image"]');
    var preview = form.querySelector('.image-preview');
    if (!fileInput || !preview) return;

    fileInput.addEventListener('change', function () {
      if (fileInput.files && fileInput.files[0]) {
        var file = fileInput.files[0];
        if (file.size > 2 * 1024 * 1024) {
          showToast('Image must be under 2 MB', 'error');
          fileInput.value = '';
          preview.style.display = 'none';
          return;
        }
        var reader = new FileReader();
        reader.onload = function (e) {
          preview.innerHTML = '<img src="' + e.target.result + '" alt="Preview">';
          preview.style.display = 'block';
        };
        reader.readAsDataURL(file);
      } else {
        preview.style.display = 'none';
      }
    });
  }

  /* read file as base64 string (data URL stripped to raw base64) */
  function readFileAsBase64(file) {
    return new Promise(function (resolve, reject) {
      var reader = new FileReader();
      reader.onload = function () { resolve(reader.result); };
      reader.onerror = function () { reject(new Error('Failed to read file')); };
      reader.readAsDataURL(file);
    });
  }

  /* --- acknowledgement slip: fill in and reveal --- */
  function showAcknowledgement(data) {
    var slip = document.getElementById('acknowledgement-slip');
    if (!slip) return;

    slip.classList.remove('print-only');
    slip.removeAttribute('hidden');

    slip.innerHTML =
      '<div class="print-area">' +
        '<h2 style="text-align:center;margin-bottom:1rem;font-family:var(--font-heading)">ACKNOWLEDGEMENT SLIP — LOST PROPERTY REGISTRATION</h2>' +
        '<div style="text-align:center;margin-bottom:1.25rem;"><span class="reg-number" style="font-size:1.2rem;padding:0.4rem 1rem;">' + (data.registration_number || '—') + '</span></div>' +
        '<div class="slip-row"><span class="slip-label">Date of Filing</span><span>' + formatDate(data.created_at || new Date().toISOString()) + '</span></div>' +
        '<div class="slip-row"><span class="slip-label">Applicant Name</span><span>' + (data.applicant_name || '—') + '</span></div>' +
        '<div class="slip-row"><span class="slip-label">Report Type</span><span><strong style="text-transform:uppercase;">' + (data.type === 'lost' ? 'Lost Property' : 'Unclaimed / Custody Property') + '</strong></span></div>' +
        '<div class="slip-row"><span class="slip-label">Property Category</span><span>' + (data.category || '—') + '</span></div>' +
        '<div class="slip-row"><span class="slip-label">Item Title</span><span>' + (data.title || '—') + '</span></div>' +
        '<div class="slip-row"><span class="slip-label">Police Station / Jurisdiction</span><span>' + (data.police_station || '—') + '</span></div>' +
        '<div class="disclaimer-box" style="margin: 1.5rem 0;">' +
          '<strong>⚠ STATUTORY NOTICE:</strong> This document is a computer-generated administrative acknowledgement for lost property registration. ' +
          'This is <strong>NOT</strong> a First Information Report (FIR). For criminal matters such as theft, robbery, or extortion, please visit your jurisdictional police station in person.' +
        '</div>' +
        '<div style="display:flex;gap:1rem;justify-content:center;margin-top:1.5rem;">' +
          '<button type="button" class="btn btn-primary screen-only" onclick="window.print()">🖨 Print Official Acknowledgement</button>' +
          '<a href="index.html" class="btn btn-secondary screen-only">Back to Notice Board</a>' +
        '</div>' +
      '</div>';

    slip.style.display = 'block';
    slip.scrollIntoView({ behavior: 'smooth' });
  }

  /* helper: set text of element by id */
  function setText(id, text) {
    var el = document.getElementById(id);
    if (el) el.textContent = text !== undefined && text !== null ? text : '—';
  }


  /* ==========================================================
     Logout
     ========================================================== */

  function initLogout() {
    var logoutBtns = document.querySelectorAll('#logout-btn, #nav-logout, [data-action="logout"]');
    logoutBtns.forEach(function (logoutBtn) {
      logoutBtn.addEventListener('click', async function (e) {
        e.preventDefault();
        try {
          await api('/api/auth/logout', { method: 'POST' });
          currentUser = null;
          showToast('Logged out', 'info');
          setTimeout(function () { window.location.href = '/'; }, 500);
        } catch (err) {
          showToast(err.message, 'error');
        }
      });
    });
  }


  /* ==========================================================
     Init — wire up whichever page we're on
     ========================================================== */

  document.addEventListener('DOMContentLoaded', async function () {
    initHamburger();
    await checkAuth();
    initLogout();

    /* --- page detection: look at the body's data attribute or known element IDs --- */
    var page = document.body.dataset.page;

    if (page === 'home' || document.getElementById('properties-grid')) {
      initHomePage();
    }

    if (page === 'report-lost' || document.getElementById('report-lost-form')) {
      initReportLostPage();
    }

    if (page === 'report-unclaimed' || document.getElementById('report-unclaimed-form')) {
      initReportUnclaimedPage();
    }

    if (page === 'property' || document.getElementById('property-detail')) {
      initPropertyDetailPage();
    }

    if (page === 'login' || document.getElementById('login-form')) {
      initLoginPage();
    }

    if (page === 'register' || document.getElementById('register-form')) {
      initRegisterPage();
    }

    if (page === 'dashboard' || document.getElementById('citizen-dashboard')) {
      initDashboardPage();
    }

    if (page === 'police-dashboard' || document.getElementById('police-dashboard')) {
      initPoliceDashboardPage();
    }

    /* tabs on any page that has them */
    initTabs();
  });

})();
