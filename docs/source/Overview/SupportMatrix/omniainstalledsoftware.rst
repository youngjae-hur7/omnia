Software Installed by Omnia
===========================

   .. csv-table:: Softwares installed by Omnia
      :file: ../../Tables/omnia_installed_software.csv
      :header-rows: 1
      :keepspace:

   .. raw:: html

       <details>
       <summary>Click to view details for RHEL/Rocky</summary>
            +----------------+-----------------------------------+------------------------------------------------+
            | GPU Make       | Models supported by Omnia         | Models validated with current version of Omnia |
            +================+===================================+================================================+
            | NVIDIA         | T4, A10, A30, A100, H100, L40     | A100, L40                                      |
            +----------------+-----------------------------------+------------------------------------------------+
            | AMD            | MI100, MI200, MI210, MI300X       | MI200, MI210, MI300X                           |
            +----------------+-----------------------------------+------------------------------------------------+
            | Intel          | Gaudi 3                           | Gaudi 3                                        |
            +----------------+-----------------------------------+------------------------------------------------+
       </details>

   .. raw:: html

       <details>
       <summary>Click to view details for Ubuntu 22.04</summary>

       .. csv-table:: Softwares installed by Omnia
          :file: ../../Tables/omnia_installed_software.csv
          :header-rows: 1
          :keepspace:

       </details>


   .. raw:: html

      <style>
      .accordion {
        background-color: #eee;
        color: #444;
        cursor: pointer;
        padding: 18px;
        width: 100%;
        border: none;
        text-align: left;
        outline: none;
        font-size: 15px;
        transition: 0.4s;
      }

      .active, .accordion:hover {
        background-color: #ccc;
      }

      .panel {
        padding: 0 18px;
        display: none;
        background-color: white;
        overflow: hidden;
      }
      </style>

   .. raw:: html

      <button class="accordion">RHEL/Rocky</button>
      <div class="panel">
        <p>Content for section 1.</p>
      </div>

      <button class="accordion">Ubuntu 22.04</button>
      <div class="panel">
        <p>Content for section 2.</p>
      </div>

      <button class="accordion">Ubuntu 24.04</button>
      <div class="panel">
        for section 3.</p>
      </div>

   .. raw:: html

      <script>
      var acc = document.getElementsByClassName("accordion");
      var i;

      for (i = 0; i < acc.length; i++) {
        acc[i].addEventListener("click", function() {
          this.classList.toggle("active");
          var panel = this.nextElementSibling;
          if (panel.style.display === "block") {
            panel.style.display = "none";
          } else {
            panel.style.display = "block";
          }
        });
      }
      </script>





