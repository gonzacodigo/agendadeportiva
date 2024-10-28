const urlAgenda = "https://agendadeportiva.onrender.com/agenda"; // Cambia a la URL correcta de tu endpoint

document.addEventListener("DOMContentLoaded", function() {
  obtenerAgenda();
});

function obtenerAgenda() {
  const cargando = document.getElementById('cargando');
  cargando.textContent = "Cargando...";

  fetch(urlAgenda)
    .then(response => {
      if (!response.ok) {
        throw new Error("Error al obtener la agenda deportiva");
      }
      return response.json();
    })
    .then(data => {
      cargando.textContent = "";
      mostrarAgenda(data);
    })
    .catch(error => {
      cargando.textContent = "";
      console.error(error);
    });
}

function mostrarAgenda(eventos) {
  const agendaContenedor = document.getElementById("agenda-deportiva");
  agendaContenedor.innerHTML = "";

  // Agrupar eventos por torneo
  const agendaPorTorneo = eventos.reduce((acc, evento) => {
    const torneo = evento.torneo || "Otros";
    if (!acc[torneo]) acc[torneo] = [];
    acc[torneo].push(evento);
    return acc;
  }, {});

  // Ordenar y mostrar por torneo
  Object.keys(agendaPorTorneo).forEach(torneo => {
    const torneoDiv = document.createElement("div");
    torneoDiv.classList.add("torneo");

    const torneoTitulo = document.createElement("h2");
    torneoTitulo.textContent = torneo;
    torneoTitulo.classList.add("torneo-titulo");
    torneoDiv.appendChild(torneoTitulo);

    // Mostrar eventos del torneo
    agendaPorTorneo[torneo].forEach(evento => {
      // Asumimos que los arrays `equipos`, `time` y `canales` tienen la misma longitud
      for (let i = 0; i < evento.equipos.length; i++) {
        const eventoDiv = document.createElement("div");
        eventoDiv.classList.add("evento-card");

        const equipos = document.createElement("p");
        equipos.textContent = `Equipos: ${evento.equipos[i]}`;
        equipos.classList.add("evento-equipos");

        const horario = document.createElement("p");
        horario.textContent = `Hora: ${evento.time[i]}`;
        horario.classList.add("evento-horario");

        const canales = document.createElement("p");
        canales.textContent = `Canales: ${evento.canales ? evento.canales.join(", ") : "N/A"}`;
        canales.classList.add("evento-canales");

        eventoDiv.appendChild(equipos);
        eventoDiv.appendChild(horario);
        eventoDiv.appendChild(canales);

        torneoDiv.appendChild(eventoDiv);
      }
    });

    agendaContenedor.appendChild(torneoDiv);
  });
}
