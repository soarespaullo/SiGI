// PÁGINA DE EDITAR MEMBROS...

// Mostrar/ocultar campo de cônjuge
document.getElementById("estadoCivil").addEventListener("change", function() {
  if (this.value === "Casado") {
    document.getElementById("conjugeField").style.display = "block";
  } else {
    document.getElementById("conjugeField").style.display = "none";
  }
});

// ✅ Verificar estado civil ao carregar a página
window.addEventListener("DOMContentLoaded", function() {
  var estadoCivil = document.getElementById("estadoCivil").value;
  if (estadoCivil === "Casado") {
    document.getElementById("conjugeField").style.display = "block";
  }
});

// Habilitar edição
document.getElementById("habilitarEdicao").addEventListener("click", function() {
  document.querySelectorAll("#formEditar input, #formEditar select, #formEditar textarea").forEach(function(el) {
    el.removeAttribute("readonly");
    el.removeAttribute("disabled"); // ✅ reativa selects, checkbox e campo de foto
  });
  // mostrar botão salvar
  document.getElementById("salvarBtn").classList.remove("d-none");
  // esconder botão habilitar
  this.style.display = "none";
});

// Aplicar máscaras (usando jQuery Mask Plugin)
$(document).ready(function(){
  $('#telefone').mask('(00) 00000-0000');
  $('#cpf').mask('000.000.000-00');
  $('#rg').mask('00.000.000-0');
  $('#cep').mask('00000-000');
});
