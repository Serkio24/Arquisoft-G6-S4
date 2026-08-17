let formato = document.getElementById('formato');
let inputTareas = document.getElementById('tarea');
let lista = document.getElementById('lista');
let filtro = document.getElementById('filtro')
let botonBorrar = document.getElementById('borrar')
let contador = document.getElementById('contador')
let prioridad = document.getElementById('prioridad')

let tareas = JSON.parse(localStorage.getItem('tareas')) || [];


function guardarTareas() {
    localStorage.setItem('tareas', JSON.stringify(tareas));
}

formato.addEventListener('submit', (e) => {

    e.preventDefault();
    const nuevaTarea = inputTareas.value.trim();
    
    if(nuevaTarea === ""){
        return("La tarea no puede estar vacia");
    }

    let tareaAgregar = {id: Date.now(), tarea: nuevaTarea, completada: false, prioridad: prioridad.value};
    tareas.push(tareaAgregar);
    guardarTareas();
    renderizarTareas();
    inputTareas.value = "";
});

lista.addEventListener('change', (e) =>{
    if(e.target.type !== "checkbox") return;

    //Como estoy mirando a un al checkbox tengo que subir hasta el li, donde ahí si esta la info 
    //del id, por eso hay que usar closest
    const id = Number(e.target.closest("li").dataset.id);
    const tarea = tareas.find(t => t.id === id);
    tarea.completada = e.target.checked
    guardarTareas();
    renderizarTareas();
    
});

botonBorrar.addEventListener('click', () =>{
    //borro las tareas que están completadas filtrando
    tareas = tareas.filter(t => t.completada === false)
    guardarTareas();
    renderizarTareas();
});

filtro.addEventListener('change', () => {
    renderizarTareas();
});

function renderizarTareas() {
    lista.innerHTML = "";
    
    let visibles = tareas;

    const prioridades = {"alta": 1, "media": 2, "baja": 3};
    visibles = [...visibles].sort((a, b) => prioridades[a.prioridad] - prioridades[b.prioridad]);
    

    if(filtro.value === "pendientes") {
        visibles = tareas.filter( t => t.completada === false );
    }
    else if(filtro.value === "completadas") {
        visibles = tareas.filter(t => t.completada === true);
    }
    visibles.forEach((tarea) => {

        const li = document.createElement("li");
        li.dataset.id = tarea.id;

        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.checked = tarea.completada;

        const contenido = document.createElement("span");
        contenido.textContent = tarea.tarea;

        const prioridad = document.createElement("prioridad");
        prioridad.textContent = tarea.prioridad;

        li.append(checkbox, contenido," - Prioridad: ", prioridad);
        lista.append(li);
    });

    const stats = estadisticas();
    contador.textContent= `Total ${stats.total}, Completadas ${stats.completadas}, Pendientes ${stats.pendientes}, Porcentaje completadas ${stats.porcentajeCompletadas}%`

}

function estadisticas() {
    const total = tareas.reduce((acc, tarea) =>{
        acc.total++;
        if(tarea.completada){
            acc.completadas++;
        } 
        else{
            acc.pendientes++;
        }
        return acc;
    }, {total: 0, completadas: 0, pendientes: 0});
    
    if(total.total !== 0) {
        total.porcentajeCompletadas = (total.completadas / total.total) * 100;
    }
    else {
        total.porcentajeCompletadas = 0;
    }
   return total;
}
renderizarTareas();