# Abaqus_plugin_rp_mid_circle_coupling
Plugins allows Abaqus users to create an RP at the middle of a circle and create a kinematic coupling between the circle and this new RP.

Developped in collaboration with [simbased.com](www.simbased.com)

You can install a plugin following this tutorial -- https://www.youtube.com/watch?v=wQ26PCPBynQ

In order to use this plugin, you have to define minimum radius and maximum radius you wish to target. The script will then loop over every instances in your assembly and add a reference point in the middle of every circle satisfying the min / max radius condition. During this loop, it creates sets to ease edition afterwards.

The plugin only shows up in these modules : ['Assembly','Step','Interaction', 'Load'].

I added an experimental feature which can target oval circles and create an RP approximately at the centre.

Use at your own risk.
