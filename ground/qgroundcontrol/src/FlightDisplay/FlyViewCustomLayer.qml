/****************************************************************************
 *
 * (c) 2009-2020 QGROUNDCONTROL PROJECT <http://www.qgroundcontrol.org>
 *
 * QGroundControl is licensed according to the terms in the file
 * COPYING.md in the root of the source code directory.
 *
 ****************************************************************************/

import QtQuick                  2.12
import QtQuick.Controls         2.4
import QtQuick.Dialogs          1.3
import QtQuick.Layouts          1.12

import QtLocation               5.3
import QtPositioning            5.3
import QtQuick.Window           2.2
import QtQml.Models             2.1

import QGroundControl               1.0
import QGroundControl.Airspace      1.0
import QGroundControl.Airmap        1.0
import QGroundControl.Controllers   1.0
import QGroundControl.Controls      1.0
import QGroundControl.FactSystem    1.0
import QGroundControl.FlightDisplay 1.0
import QGroundControl.FlightMap     1.0
import QGroundControl.Palette       1.0
import QGroundControl.ScreenTools   1.0
import QGroundControl.Vehicle       1.0

import QGroundControl.CustomPlugins.Custom_Example 1.0


// To implement a custom overlay copy this code to your own control in your custom code source. Then override the
// FlyViewCustomLayer.qml resource with your own qml. See the custom example and documentation for details.
Item {
    id: _root

    property var parentToolInsets               // These insets tell you what screen real estate is available for positioning the controls in your overlay
    property var totalToolInsets:   _toolInsets // These are the insets for your custom overlay additions
    property var mapControl

    QGCToolInsets {
        id:                         _toolInsets
        leftEdgeCenterInset:    0
        leftEdgeTopInset:           0
        leftEdgeBottomInset:        0
        rightEdgeCenterInset:   0
        rightEdgeTopInset:          0
        rightEdgeBottomInset:       0
        topEdgeCenterInset:       0
        topEdgeLeftInset:           0
        topEdgeRightInset:          0
        bottomEdgeCenterInset:    0
        bottomEdgeLeftInset:        0
        bottomEdgeRightInset:       0
    }

    // ** Example on how to insert a Button with some logic using only QML ** //
    // In this case, our pop-up button will open up a pop-up message.
    MessageDialog {
        id: msg
        title: "UAS @ UCLA"
        text: "Example mod with QGroundControl"
        onAccepted: visible = false
    }

    Button {
        id: custom_button
        text: "Pop-up Message"
        width: 200
        height: 100
        x: 10
        y: 500
        onClicked: {
            msg.open()
        }
    }
    // ********************************************************************* //


    // ** Example on how to implement a custom QML element. ** //
    // Here, "Custom_Example" is a QML element defined by the
    // "Custom_Example" C++ class in "custom_example.h" and "custom_example.cpp"
    Custom_Example
    {
        id: custom_example_element

        // When the button below prints the debug message using
        // this Custom_Example element, the debug message function
        // emits this signal.
        onMessage_printed: custom_example_msg_dialog.open()
    }

    MessageDialog {
        id: custom_example_msg_dialog
        title: "UAS @ UCLA"
        text: "This message dialog box comes from the \"message_printed()\" signal in the Custom_Example class."
        onAccepted: visible = false
    }

    Button {
        id: custom_example_button
        text: "Custom Example Button"
        width: 200
        height: 100
        x: 10
        y: 700
        onClicked: {
            // Here, we are calling the "print_message()" function in Custom_Example.
            // "print_message()" is a Slot.
            custom_example_element.print_message()
        }

    }
    // ********************************************************* //

}
