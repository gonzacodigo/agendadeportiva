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

function mostrarAgenda(noticias) {
  const agendaContenedor = document.getElementById("agenda-deportiva");
  agendaContenedor.innerHTML = "";

  // Agrupar noticias por torneo
  const agendaPorTorneo = noticias.reduce((acc, noticia) => {
    const torneo = noticia.torneo || "Otros";
    if (!acc[torneo]) acc[torneo] = [];
    acc[torneo].push(noticia);
    return acc;
  }, {});

  // Ordenar y mostrar por torneo
  Object.keys(agendaPorTorneo).forEach(torneo => {
    const torneoDiv = document.createElement("div");
    torneoDiv.classList.add("torneo");

    const torneoTitulo = document.createElement("h2");
    torneoTitulo.textContent = torneo;
    torneoTitulo.classList.add("torneo-titulo"); // Nueva clase para el título del torneo
    torneoDiv.appendChild(torneoTitulo);

    // Ordenar por horario
    agendaPorTorneo[torneo].sort((a, b) => (a.time > b.time ? 1 : -1));

    agendaPorTorneo[torneo].forEach(evento => {
      const eventoDiv = document.createElement("div");
      eventoDiv.classList.add("evento-card"); // Nueva clase para la tarjeta del evento

      const equipos = document.createElement("p");
      equipos.textContent = `${evento.equipos}`;
      equipos.classList.add("evento-equipos"); // Nueva clase para equipos

      const horario = document.createElement("p");
      horario.textContent = `Hora: ${evento.time}`;
      horario.classList.add("evento-horario"); // Nueva clase para el horario

      const canales = document.createElement("p");
      canales.textContent = `Canales: ${evento.canales.join(", ")}`;
      canales.classList.add("evento-canales"); // Nueva clase para canales

      eventoDiv.appendChild(equipos);
      eventoDiv.appendChild(horario);
      eventoDiv.appendChild(canales);

      torneoDiv.appendChild(eventoDiv);
    });

    agendaContenedor.appendChild(torneoDiv);
  });
}
