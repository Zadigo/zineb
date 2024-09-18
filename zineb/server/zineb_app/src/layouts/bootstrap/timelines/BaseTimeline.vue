<template>
  <ul class="timeline">
    <li>
      <div class="timeline-badge"></div>
      <div class="timeline-panel">
        <div class="timeline-preview"><img src="assets/images/blog/1.jpg" alt=""></div>
        <div class="timeline-body">
          <h6>Front-End Framework</h6>
          <p>Map where your photos were taken and discover local points of interest. Map where your photos. Map where your photos were taken and discover.</p>
          <p><a href="#">Read more</a></p>
        </div>
      </div>
    </li>
    <div class="timeline-top"></div>
    <div class="timeline-bottom"></div>
  </ul>
</template>


<style scoped>
.timeline {
  list-style: none;
  position: relative;
  padding: 50px 0 50px;
  margin: 0;
}

.timeline:before {
  position: absolute;
  background: #f0f0f0;
  bottom: 0;
  left: 50%;
  top: 0;
  content: "";
  width: 3px;
  margin-left: -1.5px;
}

.timeline>li {
  margin-bottom: 50px;
  position: relative;
}

.timeline>li:after,
.timeline>li:before {
  content: "";
  display: table;
}

.timeline>li:after {
  clear: both;
}

.timeline>li>.timeline-badge {
  position: absolute;
  background: #fff;
  border: 3px solid #f0f0f0;
  border-radius: 100%;
  height: 20px;
  width: 20px;
  margin-left: -10px;
  text-align: center;
  z-index: 1;
  left: 50%;
  top: 32px;
}

.timeline>li>.timeline-panel {
  position: relative;
  /* border: 1px solid #f0f0f0; */
  background: #fff;
  /* border-radius: .1875rem; */
  border-radius: .25em;
  box-shadow: 0 0 60px 0 rgb(0 0 0 / 7%);
  transition: .3s ease-in-out;
  float: left;
  width: 46%;
}

.timeline>li>.timeline-panel:before {
  position: absolute;
  background: #f0f0f0;
  right: -38px;
  top: 40px;
  transition: .3s ease-in-out;
  content: " ";
  width: 37px;
  height: 3px;
  display: block;
}

.timeline>li>.timeline-panel .timeline-body {
  padding: 40px 45px;
}

.timeline>li>.timeline-panel *:last-child {
  margin-bottom: 0;
}

.timeline-top:before,
.timeline-bottom:before {
  background: #f0f0f0;
  position: absolute;
  height: 3px;
  width: 50px;
  display: block;
  content: "";
  bottom: 0;
  left: 50%;
  margin-left: -25px;
}

.timeline-top:before {
  top: 0;
}
</style>
