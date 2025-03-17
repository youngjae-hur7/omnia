Software Installed by Omnia
===========================

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
           .. csv-table:: Softwares installed by Omnia
              :file: ../../Tables/omnia_installed_software.csv
              :header-rows: 1
              :keepspace:
      </div>

      <button class="accordion">Ubuntu 22.04</button>
      <div class="panel">
        <p>

        .. csv-table:: Softwares installed by Omnia
           :file: ../../Tables/omnia_installed_software.csv
           :header-rows: 1
           :keepspace:

        </p>
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


 .. raw:: html

 .. dropdown:: RHEL/Rocky
     :animate: fade-in
     .. csv-table:: Softwares installed by Omnia
           :file: ../../Tables/omnia_installed_software.csv
           :header-rows: 1
           :keepspace:


