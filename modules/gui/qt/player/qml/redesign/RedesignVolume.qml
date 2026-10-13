// SPDX-License-Identifier: GPL-2.0-or-later
import QtQuick
import QtQuick.Templates as T
import QtQuick.Controls.Basic as C

T.Slider {
    id: root
    property real scaleFactor: 1
    property color accentColor: "#d37918"
    property bool lightTheme: false
    property bool muted: false
    readonly property RedesignTheme theme: RedesignTheme { scaleFactor: root.scaleFactor; lightTheme: root.lightTheme; accentColor: root.accentColor }
    implicitWidth: theme.dp(90)
    implicitHeight: theme.dp(28)
    from: 0
    to: 1.25
    stepSize: 0.05
    focusPolicy: Qt.StrongFocus
    hoverEnabled: true
    Accessible.name: qsTr("Volume")
    padding: 0
    handle: Item { width: 0; height: 0 }
    background: Item {
        Item {
            id: cone
            anchors.fill: parent
            opacity: root.muted ? 0.3 : 1
            // VLC's static Qt disables Canvas. Preserve the original path and
            // colors through its already-supported SVG image plugin.
            readonly property string shape: "M2 9.8 L88 1 Q90 1 90 4 L90 24 Q90 27 88 27 L2 18.2 Q0 18.2 0 14 Z"
            function svg(fill, defs) {
                return "data:image/svg+xml;utf8," + encodeURIComponent(
                    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 90 28">'
                    + (defs || "") + '<path d="' + shape + '" fill="' + fill + '"/></svg>')
            }
            Image {
                anchors.fill: parent
                source: cone.svg("#090909", "")
                sourceSize: Qt.size(width * Screen.devicePixelRatio, height * Screen.devicePixelRatio)
            }
            Item {
                x: 2; y: 2
                width: Math.max(0, root.position * (cone.width - 4))
                height: Math.max(0, cone.height - 4)
                clip: true
                Image {
                    x: -2; y: -2
                    width: cone.width; height: cone.height
                    sourceSize: Qt.size(width * Screen.devicePixelRatio, height * Screen.devicePixelRatio)
                    source: cone.svg("url(#volume)", '<defs><linearGradient id="volume"><stop stop-color="#6d9c00"/><stop offset="0.7" stop-color="#d4b400"/><stop offset="1" stop-color="#d37918"/></linearGradient></defs>')
                }
            }
        }
        Rectangle {
            anchors.fill: parent
            color: "transparent"
            radius: theme.dp(4)
            border.width: root.visualFocus ? theme.dp(1) : 0
            border.color: theme.accent
        }
    }
    C.ToolTip.visible: root.hovered || root.visualFocus || root.pressed
    C.ToolTip.text: qsTr("%1%").arg(Math.round(value * 100))
}
