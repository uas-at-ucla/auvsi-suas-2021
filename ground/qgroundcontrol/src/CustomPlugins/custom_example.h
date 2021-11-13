#ifndef CUSTOM_EXAMPLE_H
#define CUSTOM_EXAMPLE_H

#include <QObject>
#include <QString>
#include <qqml.h>

class Custom_Example : public QObject
{

    Q_OBJECT
    // Q_PROPERTY(QString userName READ userName WRITE setUserName NOTIFY userNameChanged)
    QML_ELEMENT

public:

    // Constructor
    explicit Custom_Example(QObject *parent = nullptr);

// Slots are functions that are emitted when a signal connected to it is emitted.
// Example, a button press.
public slots:
    void print_message();


// Signals are functions that are emitted when something internal to the object has changed.
// Example, server disconnection.
signals:
    void message_printed();

};

#endif // CUSTOM_EXAMPLE_H
