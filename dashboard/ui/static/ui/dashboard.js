(function () {
  const root = document.getElementById("dashboard-root");
  if (!root) {
    return;
  }

  const stateUrl = root.dataset.stateUrl;
  const kafkaUrls = {
    raw: root.dataset.kafkaRawUrl,
    processed: root.dataset.kafkaProcessedUrl,
  };

  const REFRESH_INTERVAL = 5000;
  const KAFKA_INTERVAL = 8000;

  const eventsConsole = root.querySelector('[data-console-log="events"]');

  const logEvent = (level, message) => {
    if (!eventsConsole) {
      return;
    }

    const entry = document.createElement("div");
    entry.className = `console-entry console-entry--${level}`;

    const meta = document.createElement("div");
    meta.className = "console-entry__meta";
    const timestamp = new Date().toISOString();
    meta.textContent = `[${level.toUpperCase()}] ${timestamp}`;

    const pre = document.createElement("pre");
    pre.textContent = message;

    entry.append(meta, pre);
    eventsConsole.append(entry);
    eventsConsole.scrollTop = eventsConsole.scrollHeight;
  };

  const escapeHtml = (value) => {
    const div = document.createElement("div");
    div.textContent = value;
    return div.innerHTML;
  };

  const updateServiceCard = (service) => {
    const card = root.querySelector(`[data-service="${service.key}"]`);
    if (!card) {
      return;
    }

    const badge = card.querySelector("[data-phase]");
    if (badge) {
      const phase = (service.phase || "unknown").toLowerCase();
      badge.textContent = phase.toUpperCase();
      badge.className = `phase-badge phase-${phase}`;
    }

    const iterations = card.querySelector("[data-iterations]");
    if (iterations) {
      iterations.textContent = `Iterations: ${service.iterations ?? 0}`;
    }

    const errorNode = card.querySelector("[data-last-error]");
    if (errorNode) {
      const span = errorNode.querySelector("span") || errorNode;
      if (service.last_error) {
        span.textContent = service.last_error;
        errorNode.hidden = false;
      } else {
        span.textContent = "";
        errorNode.hidden = true;
      }
    }

    const metricsList = card.querySelector("[data-metrics]");
    if (metricsList && Array.isArray(service.metrics)) {
      metricsList.innerHTML = service.metrics
        .map(
          (metric) => `
            <li>
              <span class="metric-label">${escapeHtml(metric.label ?? "")}</span>
              <span class="metric-value">${metric.value ?? "—"}</span>
            </li>
          `,
        )
        .join("");
    }
  };

  const refreshState = async () => {
    if (!stateUrl) {
      return;
    }

    try {
      const response = await fetch(stateUrl, { headers: { "Cache-Control": "no-cache" } });
      if (!response.ok) {
        throw new Error(`${response.status} ${response.statusText}`);
      }
      const payload = await response.json();
      if (Array.isArray(payload.services)) {
        payload.services.forEach(updateServiceCard);
      }
    } catch (error) {
      logEvent("error", `State refresh failed: ${error.message}`);
    }
  };

  const renderKafkaMessages = (panel, messages) => {
    const log = panel.querySelector("[data-console-log]");
    if (!log) {
      return;
    }

    if (!messages.length) {
      log.innerHTML = '<div class="console-placeholder">No messages yet.</div>';
      return;
    }

    log.innerHTML = messages
      .map(
        (entry) => `
          <div class="console-entry">
            <div class="console-entry__meta">[p${entry.partition} · offset ${entry.offset}] ${entry.timestamp ?? ""}</div>
            <pre>${escapeHtml(entry.value ?? "")}</pre>
          </div>
        `,
      )
      .join("");
  };

  const refreshKafka = async (stream) => {
    const panel = root.querySelector(`[data-kafka-console="${stream}"]`);
    if (!panel) {
      return;
    }

    // Skip auto refresh when the panel is collapsed
    if (panel.tagName === "DETAILS" && !panel.open) {
      return;
    }

    const url = kafkaUrls[stream];
    if (!url) {
      return;
    }

    try {
      const response = await fetch(url, { headers: { "Cache-Control": "no-cache" } });
      if (!response.ok) {
        throw new Error(`${response.status} ${response.statusText}`);
      }
      const payload = await response.json();
      if (Array.isArray(payload.messages)) {
        renderKafkaMessages(panel, payload.messages);
      }
    } catch (error) {
      logEvent("error", `Kafka tail (${stream}) failed: ${error.message}`);
    }
  };

  root.addEventListener("click", (event) => {
    const target = event.target;
    if (!(target instanceof HTMLElement)) {
      return;
    }

    const action = target.dataset.action;
    if (!action) {
      return;
    }

    if (action === "refresh-tail") {
      const stream = target.dataset.stream;
      if (stream) {
        refreshKafka(stream);
      }
    } else if (action === "clear-console" && eventsConsole) {
      eventsConsole.innerHTML = '<div class="console-placeholder">Console cleared.</div>';
    }
  });

  if (stateUrl) {
    refreshState();
    setInterval(refreshState, REFRESH_INTERVAL);
  }

  ["raw", "processed"].forEach((stream) => {
    if (kafkaUrls[stream]) {
      refreshKafka(stream);
      setInterval(() => refreshKafka(stream), KAFKA_INTERVAL);
    }
  });
})();
