from enum import Enum


class States(Enum):
    alvo = 'av'
    ctrl_ausente = None
    ctrl_positivo = True
    ctrl_negativo = False

    def __eq__(self, other):
        other_value = other

        if type(other_value) is self:
            other_value = other_value.value

        return other_value == self.value

    def __repr__(self):
        if self.value == self.ctrl_positivo:
            return 'Positivo'

        if self.value == self.ctrl_negativo:
            return 'Negativo'

        if self.value == self.ctrl_ausente:
            return 'Ausente'

        # return str(self.value)
        return 'Alvo'

    def __str__(self):
        return self.__repr__()
