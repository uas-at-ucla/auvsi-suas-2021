#include "custom_example.h"
#include <QDebug>

Custom_Example::Custom_Example(QObject *parent) : QObject(parent)
{
}

void Custom_Example::print_message()
{
    qDebug() << "Qt Slot call from Custom_Example::print_message()";

    emit message_printed();
}
