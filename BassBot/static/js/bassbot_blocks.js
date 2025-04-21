/* static/js/bassbot_blocks.js  ──────────────────────────────────────────
   New dropdown blocks: servo_control & fret_control
   Works with Blockly 10/11 and the Python generator.
*/

(function() {
  /* === Block definitions =========================================== */
  Blockly.defineBlocksWithJsonArray([
    /* Servo control -------------------------------------------------- */
    {
      "type": "servo_control",
      "message0": "servo %1 %2",
      "args0": [
        {
          "type": "field_dropdown",
          "name": "SERVO",
          "options": [
            ["servoE", "servoE"],
            ["servoA", "servoA"],
            ["servoD", "servoD"],
            ["servoG", "servoG"]
          ]
        },
        {
          "type": "field_dropdown",
          "name": "ACTION",
          "options": [
            ["pick", "pick"],
            ["damp", "damp"],
            ["sustain", "sustain"]
          ]
        }
      ],
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#D39D2A",
      "tooltip": "Pick, damp, or sustain the chosen string."
    },

    /* Fret control --------------------------------------------------- */
    {
      "type": "fret_control",
      "message0": "fret %1 %2",
      "args0": [
        {
          "type": "field_dropdown",
          "name": "FRET",
          "options": [
            ["fret1", "fret1"],
            ["fret2", "fret2"],
            ["fret3", "fret3"],
            ["fret4", "fret4"]
          ]
        },
        {
          "type": "field_dropdown",
          "name": "STATE",
          "options": [
            ["on",  "on"],
            ["off", "off"]
          ]
        }
      ],
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#D39D2A",
      "tooltip": "Turn a fret on or off."
    },

    /* Wait block (unchanged) ---------------------------------------- */
    {
      "type": "controls_wait",
      "message0": "wait %1 seconds",
      "args0": [
        { "type": "input_value", "name": "DURATION", "check": "Number" }
      ],
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#5C81A6",
      "tooltip": "Pause execution."
    }
  ]);

  /* === Python generators ========================================== */
  const PY = Blockly.Python;

  /* Servo control generator */
  PY.forBlock['servo_control'] = blk => {
    const servo  = blk.getFieldValue('SERVO');
    const action = blk.getFieldValue('ACTION');  // pick | damp | sustain
    return `bass.${servo}.${action}()\n`;
  };

  /* Fret control generator */
  PY.forBlock['fret_control'] = blk => {
    const fret  = blk.getFieldValue('FRET');   // fret1‑4
    const state = blk.getFieldValue('STATE');  // on | off
    return `bass.${fret}.${state}()\n`;
  };

  /* Wait generator */
  PY.forBlock['controls_wait'] = blk => {
    const dur = PY.valueToCode(blk, 'DURATION', PY.ORDER_ATOMIC) || '1';
    return `wait(${dur})\n`;
  };
})();
