document.addEventListener('DOMContentLoaded', () => {
  const map = {
    salas_top: 'salasTop',
    turnos_top: 'turnosTop',
    promedio_participantes_sala: 'promedioParticipantesSala',
    reservas_por_carrera_facultad: 'reservasPorCarreraFacultad',
    ocupacion_por_edificio: 'ocupacionPorEdificio',
    reservas_asistencias: 'reservasAsistencias',
    sanciones_por_rol_tipo: 'sancionesPorRolTipo',
    porcentaje_utilizacion: 'porcentajeUtilizacion',
    proporcion_alumnas: 'proporcionAlumnas',
    reservas_por_genero: 'reservasPorGenero',
    edad_promedio_por_edificio: 'edadPromedioPorEdificio'
  };
  document.querySelectorAll('.consulta-action').forEach(btn => {
    btn.addEventListener('click', () => {
      const key = btn.dataset.key;
      const file = map[key];
      if (file) {
        window.location.href = `../consultas/${file}.html`;
      }
    });
  });
});
